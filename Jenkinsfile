pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'harshit0400/api-health-checker'
    }
    
    stages {
        
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ✅ RUN TESTS FIRST (IMPORTANT)
        stage('Test') {
            steps {
                echo 'Running tests...'
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pip install pytest coverage'

                // generate coverage.xml
                bat 'coverage run -m pytest'
                bat 'coverage xml'
            }
        }

        // ✅ THEN SONAR
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        bat "${scannerHome}\\bin\\sonar-scanner.bat"
                    }
                }
            }
        }

        // ✅ INCREASE TIMEOUT
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
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
    }
}