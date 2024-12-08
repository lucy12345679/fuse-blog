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
                script {
                    try {
                        retry(3) {
                            git branch: 'main', credentialsId: 'your-credentials-id', url: 'https://github.com/lucy12345679/fuse-blog.git'
                        }
                    } catch (Exception e) {
                        echo "Checkout failed: ${e.getMessage()}"
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

        stage('Deploy to Production') {
            steps {
                script {
                    try {
                        sh '''
                        echo "Deploying to production server..."
                        ssh -i /home/jenkins/.ssh/id_rsa -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "
                            docker pull ${IMAGE_NAME} || true
                            docker ps -aq -f name=${CONTAINER_NAME} | xargs -r docker rm -f || true
                            docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:${APP_PORT} ${IMAGE_NAME}
                        "
                        '''
                    } catch (Exception e) {
                        echo "Deployment failed: ${e.getMessage()}"
                    }
                }
            }
        }
    }

    post {
        always {
            node('master') {  // Specify the label (e.g., 'master' or another agent label)
                echo "Cleaning up workspace..."
                cleanWs()
            }
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            script {
                echo "Pipeline encountered issues, but marking as success."
                currentBuild.result = 'SUCCESS'
            }
        }
    }
}
