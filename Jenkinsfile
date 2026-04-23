pipeline {

    agent any

    environment {
        DOCKER_IMAGE = 'harshit0400/api-health-checker'
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

     stage('Deploy with Ansible') {
    steps {
        echo 'Deploying to EC2 via Ansible...'
        bat '''
        wsl bash -c "
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID &&
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY &&
        export AWS_REGION=eu-north-1 &&
        cd /mnt/d/DEVOPS_PROJ/api-health-checker &&
        ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
        "
        '''
    }
}
    }

    post {
        success { 
            echo '✅ Pipeline succeeded — deployment complete' 
        }
        failure { 
            echo '❌ Pipeline failed — check logs above' 
        }
    }
}