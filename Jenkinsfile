pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'harshit0400/api-health-checker'
        EC2_HOST = '16.171.151.199'
        SSH_KEY = 'C:\\jenkins-credentials\\ec2-key.pem'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests with coverage...'
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pip install pytest pytest-cov'
                bat 'pytest --cov=. --cov-report=xml'
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube code analysis...'
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        bat "${scannerHome}\\bin\\sonar-scanner.bat"
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat "docker build -t %DOCKER_IMAGE%:%BUILD_NUMBER% ."
                bat "docker tag %DOCKER_IMAGE%:%BUILD_NUMBER% %DOCKER_IMAGE%:latest"
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS')]) {
                    bat '''
                        echo %DOCKER_PASS%| docker login -u %DOCKER_USER% --password-stdin
                        docker push %DOCKER_IMAGE%:latest
                    '''
                }
            }
        }
        
        stage('Deploy to EC2') {
            steps {
                echo 'Deploying to EC2...'
                bat """
                    ssh -o StrictHostKeyChecking=no -i %SSH_KEY% ubuntu@%EC2_HOST% "docker pull harshit0400/api-health-checker:latest && docker stop app || true && docker rm app || true && docker run -d -p 5001:5001 --env-file /home/ubuntu/.env --name app --restart unless-stopped harshit0400/api-health-checker:latest && docker ps | grep app"
                """
            }
        }
    }
    
    post {
        success { 
            echo '✅ Pipeline succeeded — app deployed to EC2' 
        }
        failure { 
            echo '❌ Pipeline failed — check logs above' 
        }
    }
}