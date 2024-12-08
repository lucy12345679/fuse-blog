pipeline {
    agent any

    environment {
        IMAGE_NAME = "fuse_blog_web"
        CONTAINER_NAME = "fuse_blog_web_1"
        APP_PORT = "8000"
        HOST_PORT = "8000"
        SERVER_IP = "161.35.208.242"
        SERVER_USER = "root"
    }

    stages {
        // Checkout Stage
        stage('Checkout') {
            steps {
                retry(3) { // Retry in case of transient failures
                    cleanWs() // Clean workspace before checkout
                    sh '''
                    git config --global http.postBuffer 524288000
                    git config --global http.version HTTP/1.1
                    '''
                    git branch: 'main', url: 'https://github.com/lucy12345679/fuse-blog.git'
                }
            }
        }

        // Build Docker Image
        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building Docker image..."
                docker build -t ${IMAGE_NAME} .
                '''
            }
        }

        // Run Tests
        stage('Run Tests') {
            steps {
                sh '''
                echo "Running tests in the Docker container..."
                docker run --rm ${IMAGE_NAME} pytest
                '''
            }
        }

        // Deploy to Production
        stage('Deploy') {
            steps {
                sh '''
                echo "Deploying application to production..."
                ssh -i /home/jenkins/.ssh/id_rsa -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "
                    echo 'Pulling Docker image and starting container...'
                    docker pull ${IMAGE_NAME}
                    docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm -f || true
                    docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:${APP_PORT} ${IMAGE_NAME}
                "
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
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}
