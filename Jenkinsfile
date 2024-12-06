pipeline {
    agent any

    environment {
        IMAGE_NAME = "fuse_blog_web"
        CONTAINER_NAME = "fuse_blog_web_1"
        APP_PORT = "8000"
        SERVER_IP = "161.35.208.242"
        SERVER_USER = "root"
    }

    stages {
        stage('Checkout') {
            steps {
                retry(3) {
                    cleanWs() // Ensure workspace is clean before cloning
                    git branch: 'main', url: 'https://github.com/lucy12345679/fuse-blog.git'
                }
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
                pylint apps/ || true
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
                export PYTHONPATH=$(pwd)
                export DJANGO_SETTINGS_MODULE=root.settings

                if python -m pytest --help | grep -q -- --cov; then
                    pytest --ds=root.settings --cov=apps
                else
                    echo "pytest-cov not available; running tests without coverage."
                    pytest --ds=root.settings
                fi
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

                    // Stop the container if running
                    sh '''
                    docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker stop || true
                    docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm || true
                    '''

                    echo "Running the new container..."
                    sh '''
                    docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} ${IMAGE_NAME}
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

        stage('Deploy to Production') {
            steps {
                script {
                    echo "Deploying directly to the server..."
                    sh '''
                    ssh -o StrictHostKeyChecking=no root@${SERVER_IP} "
                        cd /root || exit
                        docker pull ${IMAGE_NAME} || true
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true
                        docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} ${IMAGE_NAME}
                    "
                    '''
                }
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
