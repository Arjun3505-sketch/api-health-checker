pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'harshit0400/api-health-checker'
        EC2_HOST = '16.171.151.199'
    }

    stages {
        stage('Clone') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main',
                    url: 'https://github.com/Arjun3505-sketch/api-health-checker.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat "docker build -t %DOCKER_IMAGE%:%BUILD_NUMBER% ."
                bat "docker tag %DOCKER_IMAGE%:%BUILD_NUMBER% %DOCKER_IMAGE%:latest"
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                bat 'python --version'
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pip install pytest'
                bat 'python -m pytest tests/ -v'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing to Docker Hub...'
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
                echo 'Deploying to EC2 via SSH...'
                withCredentials([
                    sshUserPrivateKey(credentialsId: 'ec2-ssh-key', keyFileVariable: 'SSH_KEY'),
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET')
                ]) {
                    bat """
                        ssh -o StrictHostKeyChecking=no -i %SSH_KEY% ubuntu@%EC2_HOST% "/home/ubuntu/deploy.sh %AWS_KEY_ID% %AWS_SECRET% eu-north-1"
                    """
                }
            }
        }
    }

    post {
        success { echo 'Pipeline succeeded — app deployed to EC2' }
        failure { echo 'Pipeline failed — check logs above' }
    }
}