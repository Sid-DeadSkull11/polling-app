
pipeline {
    agent any

    environment {
        DOCKER_USERNAME = "siddeadskull11"
        IMAGE_NAME = "siddeadskull11/polling-app:v1"
        DOCKER_EXE = "C:\\Users\\siddh\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code is available in the Jenkins workspace'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'py -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'py -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER_EXE%" build -t %IMAGE_NAME% .'
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat '''
                    echo %DOCKER_PASS% | "%DOCKER_EXE%" login -u %DOCKER_USER% --password-stdin
                    '''
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                bat '"%DOCKER_EXE%" push %IMAGE_NAME%'
            }
        }
    }

    post {
        success {
            echo 'V1 image successfully pushed to Docker Hub!'
        }
        failure {
            echo 'V1 pipeline failed. Check the console output.'
        }
    }
}