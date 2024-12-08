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
                retry(3) { // Retry for transient issues
                    git branch: 'main', credentialsId: 'your-credentials-id', url: 'https://github.com/lucy12345679/fuse-blog.git'
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
                        currentBuild.result = 'FAILURE'
                        error("Stopping pipeline due to Docker build failure.")
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    try {
                        sh '''
                        echo "Running tests in the Docker container..."
                        docker run --rm ${IMAGE_NAME} pytest
                        '''
                    } catch (Exception e) {
                        echo "Tests failed: ${e.getMessage()}"
                        currentBuild.result = 'FAILURE'
                        error("Stopping pipeline due to test failure.")
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
                        docker run --rm ${IMAGE_NAME} python manage.py collectstatic --noinput
                        '''
                    } catch (Exception e) {
                        echo "Static file collection failed: ${e.getMessage()}"
                        currentBuild.result = 'FAILURE'
                        error("Stopping pipeline due to static file collection failure.")
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh '''
                    echo "Deploying application..."
                    ssh -i /home/jenkins/.ssh/id_rsa -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "
                        echo 'Pulling and running the Docker container...'
                        docker pull ${IMAGE_NAME}
                        docker ps -aq -f name=${IMAGE_NAME} | xargs -r docker rm -f || true
                        docker run -d --name ${IMAGE_NAME} -p 8000:8000 ${IMAGE_NAME}
                    "
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
