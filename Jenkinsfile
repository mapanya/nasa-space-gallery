pipeline {
    agent any

    environment {
        IMAGE_NAME = 'nasa-space-gallery'
        IMAGE_TAG  = "1.0.${BUILD_NUMBER}"
        CONTAINER  = 'nasa-space-gallery'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG -t $IMAGE_NAME:latest .'
            }
        }

        stage('Test') {
            steps {
                // Run the automated tests inside a throwaway copy of the new image.
                sh '''
                    docker run --rm --user root $IMAGE_NAME:$IMAGE_TAG \
                        sh -c "pip install --quiet --no-cache-dir -r requirements-dev.txt && python -m pytest -v"
                '''
            }
        }

        stage('Deploy') {
            steps {
                // Replace the running container with the new version.
                sh '''
                    docker rm -f $CONTAINER || true
                    docker run -d --name $CONTAINER -p 5001:5001 $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }
    }

    post {
        success {
            echo 'Build, test and deploy finished. Open http://localhost:5001'
        }
        failure {
            echo 'The pipeline failed. Open the stage shown in red to read the error.'
        }
    }
}
