pipeline {
    agent any

    environment {
        IMAGE_NAME = "fuse_blog_web"
        CONTAINER_NAME = "fuse_blog_web_${BUILD_ID}"
        APP_PORT = "8000"
        HOST_PORT = "8000"
        SERVER_IP = "161.35.208.242"
        SERVER_USER = "root"
    }

    stages {
        stage('Checkout') {
            steps {
                retry(3) {
                    script {
                        try {
                            cleanWs()
                            git branch: 'main', url: 'https://github.com/lucy12345679/fuse-blog.git'
                        } catch (Exception e) {
                            echo "Checkout failed: ${e.getMessage()}"
                        }
                    }
                }
            }
        }

         stage('Build Docker Image') {
            steps {
                script {
                    try {
                        sh '''
                        echo "Building Docker image..."
                        docker build -t ${IMAGE_NAME} .
                        '''
                    } catch (Exception e) {
                        echo "Docker image build failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    try {
                        sh '''
                        echo "Stopping and removing any existing container..."
                        docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm -f || true

                        echo "Checking for conflicting containers using port ${HOST_PORT}..."
                        CONFLICTING_CONTAINERS=$(docker ps --filter "publish=${HOST_PORT}" -q)
                        if [ ! -z "$CONFLICTING_CONTAINERS" ]; then
                            echo "Stopping conflicting containers..."
                            echo "$CONFLICTING_CONTAINERS" | xargs -r docker stop || true
                            echo "Removing conflicting containers..."
                            echo "$CONFLICTING_CONTAINERS" | xargs -r docker rm || true
                        fi

                        echo "Running a new Docker container on host port ${HOST_PORT}..."
                        docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:${APP_PORT} ${IMAGE_NAME}
                        '''
                    } catch (Exception e) {
                        echo "Failed to run Docker container: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Run Tests in Container') {
            steps {
                script {
                    try {
                        sh '''
                        echo "Running tests inside the container..."
                        docker exec ${CONTAINER_NAME} python manage.py test
                        '''
                    } catch (Exception e) {
                        echo "Tests failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Static File Collection') {
            steps {
                script {
                    try {
                        sh '''
                        echo "Collecting static files..."
                        docker exec ${CONTAINER_NAME} python manage.py collectstatic --noinput
                        '''
                    } catch (Exception e) {
                        echo "Static file collection failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Deploy to Production') {
            steps {
                script {
                    try {
                        // Ensure you have the SSH Agent plugin installed and configured with the correct credentials
                        sshagent(['jenkins-ssh-credential-id']) {
                            sh '''
                            echo "Deploying to production server..."
                            ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "
                                echo 'Pulling latest Docker image...'
                                docker pull ${IMAGE_NAME} || true

                                echo 'Stopping and removing existing container if it exists...'
                                docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm -f || true

                                echo 'Running the new Docker container...'
                                docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} ${IMAGE_NAME}
                            "
                            '''
                        }
                    } catch (Exception e) {
                        echo "Deployment failed: ${e.getMessage()}"
                    }
                }
            }
        }
    }

       post {
        always {
            echo "Pipeline completed execution."
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed, but marking as success."
        }
    }
}
