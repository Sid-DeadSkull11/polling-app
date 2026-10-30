
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        IMAGE_NAME = "siddeadskull11/polling-app:v2"

        PYTHON_EXE = "C:\\Users\\siddh\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe"

        DOCKER_EXE = "C:\\Users\\siddh\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON_EXE%" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"%PYTHON_EXE%" -m pytest -v'
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
                    credentialsId: 'dockerhub-polling-v1',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat '''
                    @echo off
                    echo %DOCKER_PASS%| "%DOCKER_EXE%" login -u %DOCKER_USER% --password-stdin
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
            echo 'V1 successfully pushed to Docker Hub!'
        }

        failure {
            echo 'V1 pipeline failed. Check Console Output.'
        }
    }
}