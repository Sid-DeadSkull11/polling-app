
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        IMAGE_NAME = "siddeadskull11/polling-app:v1"

        PYTHON_EXE = "C:\\Users\\siddh\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe"

        DOCKER_EXE = "C:\\Users\\siddh\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies'

                bat '''
                "%PYTHON_EXE%" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running automated pytest cases'

                bat '''
                "%PYTHON_EXE%" -m pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building V1 Docker image'

                bat '''
                "%DOCKER_EXE%" build -t %IMAGE_NAME% .
                '''
            }
        }

        stage('Docker Hub Login') {
            steps {
                echo 'Authenticating with Docker Hub'

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    powershell '''
                    $env:DOCKER_PASS | & $env:DOCKER_EXE login -u $env:DOCKER_USER --password-stdin

                    if ($LASTEXITCODE -ne 0) {
                        exit $LASTEXITCODE
                    }
                    '''
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing V1 image to Docker Hub'

                bat '''
                "%DOCKER_EXE%" push %IMAGE_NAME%
                '''
            }
        }
    }

    post {
        success {
            echo 'V1 pipeline completed successfully!'
            echo 'Docker image pushed to Docker Hub.'
        }

        failure {
            echo 'V1 pipeline failed. Check the Console Output.'
        }

        always {
            echo 'V1 Jenkins pipeline execution completed.'
        }
    }
}