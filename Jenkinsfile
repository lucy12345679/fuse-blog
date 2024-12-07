pipeline {
    agent any

    environment {
        IMAGE_NAME = "fuse_blog_web"
        CONTAINER_NAME = "fuse_blog_web_${BUILD_ID}"
        APP_PORT = "8000"
        SERVER_IP = "161.35.208.242"
        SERVER_USER = "root"
    }

    stages {
        stage('Checkout') {
            steps {
                retry(3) {
                    cleanWs()
                    git branch: 'main', url: 'https://github.com/lucy12345679/fuse-blog.git'
                }
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
                    sh '''
                    echo "Stopping and removing any existing container..."
                    docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm -f || true

                    echo "Checking if port ${APP_PORT} is in use..."
                    if lsof -i:${APP_PORT} -sTCP:LISTEN | grep -q ${APP_PORT}; then
                        echo "Port ${APP_PORT} is in use. Stopping the process..."
                        lsof -i:${APP_PORT} -sTCP:LISTEN | awk 'NR>1 {print $2}' | xargs -r kill -9 || true
                    fi

                    echo "Running a new Docker container..."
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
                sshagent(['jenkins-ssh-credential-id']) {
                    sh '''
                    echo "Deploying to production server..."
                    ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "
                        cd /root || exit
                        docker pull ${IMAGE_NAME} || true
                        docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm -f || true
                        docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} ${IMAGE_NAME}
                    "
                    '''
                }
            }
        }
    }

    post {
        always {
            sh '''
            echo "Cleaning up local container..."
            docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm -f || true
            '''
            echo "Cleaning up workspace..."
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Check the logs for details."
        }
    }
}
