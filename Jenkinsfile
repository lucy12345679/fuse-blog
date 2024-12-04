pipeline {
    agent any

    environment {
        IMAGE_NAME = "fuse_blog_web"
        CONTAINER_NAME = "fuse_blog_web_1"
        APP_PORT = "8000"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/lucy12345679/fuse-blog.git'
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                sh '''
                echo "Setting up virtual environment..."
                python3 -m venv .venv
                . .venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                echo "Running linting with pylint..."
                . .venv/bin/activate
                pylint --rcfile=.pylintrc apps/ || true
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                echo "Running security scan with bandit..."
                . .venv/bin/activate
                bandit -r apps/
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                echo "Running tests with pytest..."
                . .venv/bin/activate
                pytest --cov=apps || pytest apps/  # Fallback if pytest-cov is unavailable
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building Docker image..."
                docker build -t ${IMAGE_NAME} .
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    echo "Stopping and removing existing container..."
                    sh '''
                    sudo docker ps -aq -f name=${CONTAINER_NAME} | xargs -r sudo docker stop || true
                    sudo docker ps -aq -f name=${CONTAINER_NAME} | xargs -r sudo docker rm || true
                    echo "Running the new container..."
                    sudo docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} ${IMAGE_NAME}
                    '''
                }
            }
        }

        stage('Run Tests in Container') {
            steps {
                sh '''
                echo "Running tests inside the container..."
                docker exec ${CONTAINER_NAME} python manage.py test
                '''
            }
        }

        stage('Static File Collection') {
            steps {
                sh '''
                echo "Collecting static files..."
                docker exec ${CONTAINER_NAME} python manage.py collectstatic --noinput
                '''
            }
        }

        stage('Clean Up') {
            steps {
                sh '''
                echo "Cleaning up container..."
                docker stop ${CONTAINER_NAME} || true
                docker rm ${CONTAINER_NAME} || true
                '''
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace..."
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully: linting, security scan, build, tests, and static file collection!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
    }
}
