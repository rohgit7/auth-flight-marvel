pipeline {
    agent any

    environment {
        NETWORK_NAME = "auths-network"
        MONGO_NAME   = "mongo_container"
        AUTH_NAME    = "auth-service"
        SCRAPER_NAME = "flight-scraper"
    }

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
                bat 'docker network create %NETWORK_NAME% || exit 0'
            }
        }

        stage('Start MongoDB') {
            steps {
                bat 'docker rm -f %MONGO_NAME% || exit 0'
                bat 'docker run -d --name %MONGO_NAME% --network %NETWORK_NAME% -v mongo_data:/data/db -p 27017:27017 mongo'
            }
        }

        stage('Start Flight Web Scraper') {
            steps {
                bat 'docker rm -f %SCRAPER_NAME% || exit 0'
                bat 'docker run -d --name %SCRAPER_NAME% --network %NETWORK_NAME% -p 5000:5000 flight-scraper'
            }
        }

        stage('Start Auth Service') {
            steps {
                bat 'docker rm -f %AUTH_NAME% || exit 0'
                bat 'docker run -d --name %AUTH_NAME% --network %NETWORK_NAME% -e MONGO_URL=mongodb://%MONGO_NAME%:27017/auth_demo -p 3000:3000 auth-service'
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
            bat '''
            cd terraform &&
            set AWS_DEFAULT_REGION=ap-south-1 &&
            terraform init
            '''
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
            bat '''
            cd terraform &&
            set AWS_DEFAULT_REGION=ap-south-1 &&
            terraform apply -auto-approve -var="key_name=auth-flight-key"
            '''
        }
    }
}


    }

    post {
        success {
            echo "✅ Pipeline completed successfully"
            echo "🔐 Auth Service running on port 3000"
            echo "✈️ Flight Scraper accessible after login"
        }

        failure {
            echo "❌ Pipeline failed. Check logs for details."
        }
    }
}
