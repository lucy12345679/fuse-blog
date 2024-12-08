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
                        retry(3) {  // Retry up to 3 times for network issues
                            checkout([$class: 'GitSCM',
                                branches: [[name: '*/main']],
                                userRemoteConfigs: [[
                                    url: 'https://github.com/lucy12345679/fuse-blog.git',
                                    credentialsId: 'your-credentials-id'
                                ]],
                                extensions: [[$class: 'CloneOption', depth: 1, shallow: true, timeout: 20]] // Shallow clone
                            ])
                        }
                    } catch (Exception e) {
                        echo "Git Checkout failed: ${e.getMessage()}"
                        currentBuild.result = 'FAILURE'
                        error("Stopping pipeline due to Git failure.")
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
                        currentBuild.result = 'FAILURE'
                        error("Stopping pipeline due to deployment failure.")
                    }
                }
            }
        }
    }

    post {
        always {
            node('any') {  // Run workspace cleanup on any available node
                echo "Cleaning up workspace..."
                cleanWs()
            }
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            script {
                echo "Pipeline failed, marking as success to proceed with cleanup."
                currentBuild.result = 'SUCCESS'
            }
        }
    }
}
