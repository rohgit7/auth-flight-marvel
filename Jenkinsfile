pipeline {
    agent any

    stages {

        stage('Install Node Dependencies') {
            steps {
                bat 'cd auth-service && npm install'
            }
        }

        stage('Build Auth Image') {
            steps {
                bat 'docker build -t auth-service ./auth-service'
            }
        }

        stage('Build Flight Scraper Image') {
            steps {
                bat 'docker build -t flight-scraper ./flight-web-scraping'
            }
        }

        stage('Create Docker Network') {
            steps {
                bat 'docker network create auths-network || exit 0'
            }
        }

        stage('Start MongoDB') {
            steps {
                bat 'docker rm -f mongo_container || exit 0'
                bat 'docker run -d --name mongo_container --network auths-network -v mongo_data:/data/db -p 27017:27017 mongo'
            }
        }

        stage('Start Flight Web Scraper') {
            steps {
                bat 'docker rm -f flight-scraper || exit 0'
                bat 'docker run -d --name flight-scraper --network auths-network -p 5000:5000 flight-scraper'
            }
        }

        stage('Start Auth Service') {
            steps {
                bat 'docker rm -f auth-service || exit 0'
                bat 'docker run -d --name auth-service --network auths-network -e MONGO_URL=mongodb://mongo_container:27017/auth_demo -p 3000:3000 auth-service'
            }
        }

        stage('Terraform Init') {
    steps {
        withCredentials([[
            $class: 'AmazonWebServicesCredentialsBinding',
            credentialsId: 'aws-creds',
            accessKeyVariable: 'AWS_ACCESS_KEY_ID',
            secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
        ]]) {
            bat 'cd terraform'
            bat 'set AWS_DEFAULT_REGION=ap-south-1'
            bat 'terraform init'
        }
    }
}


        stage('Terraform Apply') {
    steps {
        withCredentials([[
            $class: 'AmazonWebServicesCredentialsBinding',
            credentialsId: 'aws-creds',
            accessKeyVariable: 'AWS_ACCESS_KEY_ID',
            secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
        ]]) {
            bat 'cd terraform'
            bat 'set AWS_DEFAULT_REGION=ap-south-1'
            bat 'terraform apply -auto-approve -var="key_name=auth-flight-key"'
        }
    }
}

    }

    post {
        success {
            echo '✅ Pipeline completed successfully'
        }
        failure {
            echo '❌ Pipeline failed'
        }
    }
}
