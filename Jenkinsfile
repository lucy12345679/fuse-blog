pipeline {
    agent any

    environment {
        IMAGE_NAME = "fuce_blog"
        CONTAINER_NAME = "fuce_blog"
        APP_PORT = "8000"
        DEPLOY_HOST = "161.35.208.242"
    }

    stages {
        stage('Checkout process') {
            steps {
                echo "Git clone project..."
                git branch: 'main', url: 'https://github.com/lucy12345679/fuse-blog'
            }
        }

        stage('Creating Environment') {
            steps {
                sh '''
                echo "Create virtual environment..."
                python3 -m venv .venv
                bash -c "source .venv/bin/activate && pip install -r requirements.txt"
                '''
            }
        }

        stage('Before Testing process') {
            steps {
                sh '''
                echo "Running linting with pylint..."
                bash -c "source .venv/bin/activate && pylint --rcfile=.pylintrc main/ || true"
                '''
            }
        }


        stage('Test process') {
            steps {
                sh '''
                echo "Running tests with pytest..."
                bash -c "source .venv/bin/activate && pytest --cov=main"
                '''
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'credentials', usernameVariable: 'USER', passwordVariable: 'PASSWORD')]) {
                    sh '''
                    echo "Deploying PROJECT on server..."
                    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$DEPLOY_HOST "cd fuse-blog/ && docker-compose up -d --build"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace..."
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully: Checkout process, Test process, Docker Build, and Deploy!"
        }
        failure {
            echo "Pipeline failed. Check the logs for details."
        }
    }
}
