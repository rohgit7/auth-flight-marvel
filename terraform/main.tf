provider "aws" {
  region = var.region
}

resource "aws_security_group" "app_sg" {
  name = "auth-flight-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "auth_flight" {
  ami                    = "ami-0f5ee92e2d63afc18" # Ubuntu 22.04 ap-south-1
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = <<-EOF
    #!/bin/bash
    apt update -y
    apt install -y docker.io git
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu

    cd /home/ubuntu
    git clone https://github.com/rohgit7/auth-flight-marvel.git
    cd auth-flight-marvel

    docker network create auths-network || true

    docker run -d --name mongo_container --network auths-network \
      -v mongo_data:/data/db mongo

    docker build -t flight-scraper ./flight-web-scraping
    docker build -t auth-service ./auth-service

    docker run -d --name flight-scraper --network auths-network -p 5000:5000 flight-scraper
    docker run -d --name auth-service --network auths-network \
      -e MONGO_URL=mongodb://mongo_container:27017/auth_demo \
      -p 3000:3000 auth-service
  EOF

  tags = {
    Name = "AuthFlightFreeTier"
  }
}
