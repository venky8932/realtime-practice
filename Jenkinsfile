pipeline {
  agent any

  environment {
    AWS_REGION = 'us-east-1'
    CLUSTER_NAME = 'app-eks-cluster'
    ECR_REPO = '012345678901.dkr.ecr.us-east-1.amazonaws.com/app'
    IMAGE_TAG = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/venky8932/realtime-practice.git'
      }
    }

    stage('Build Images') {
      steps {
        dir('fastapi') {
          sh 'docker build -t ${ECR_REPO}:fastapi-${IMAGE_TAG} .' 
        }
        dir('nodejs') {
          sh 'docker build -t ${ECR_REPO}:nodejs-${IMAGE_TAG} .' 
        }
        dir('worker') {
          sh 'docker build -t ${ECR_REPO}:worker-${IMAGE_TAG} .' 
        }
        dir('alert-watcher') {
          sh 'docker build -t ${ECR_REPO}:alert-watcher-${IMAGE_TAG} .' 
        }
      }
    }

    stage('Push Images') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-registry-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin ${ECR_REPO}'
        }
        sh 'docker push ${ECR_REPO}:fastapi-${IMAGE_TAG}'
        sh 'docker push ${ECR_REPO}:nodejs-${IMAGE_TAG}'
        sh 'docker push ${ECR_REPO}:worker-${IMAGE_TAG}'
        sh 'docker push ${ECR_REPO}:alert-watcher-${IMAGE_TAG}'
      }
    }

    stage('Terraform Init & Plan') {
      steps {
        dir('terraform') {
          withCredentials([usernamePassword(credentialsId: 'aws-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
            sh 'terraform init'
            sh 'terraform plan -out=tfplan'
          }
        }
      }
    }

    stage('Terraform Apply') {
      steps {
        dir('terraform') {
          withCredentials([usernamePassword(credentialsId: 'aws-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
            input message: 'Approve Terraform apply?'
            sh 'terraform apply -auto-approve tfplan'
          }
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'aws-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
          sh 'aws eks update-kubeconfig --region ${AWS_REGION} --name ${CLUSTER_NAME}'
        }
        dir('k8s') {
          sh 'kubectl apply -f secret-db.yaml'
          sh 'kubectl apply -f alert-watcher.yaml'
          sh 'kubectl apply -f fastapi-deployment.yaml'
          sh 'kubectl apply -f fastapi-service.yaml'
          sh 'kubectl apply -f nodejs-deployment.yaml'
          sh 'kubectl apply -f nodejs-service.yaml'
          sh 'kubectl apply -f worker-deployment.yaml'
          sh 'kubectl apply -f worker-service.yaml'
          sh 'kubectl apply -f fastapi-hpa.yaml'
          sh 'kubectl apply -f nodejs-hpa.yaml'
        }
      }
    }
  }

  post {
    always {
      echo 'Jenkins pipeline finished'
    }
  }
}
