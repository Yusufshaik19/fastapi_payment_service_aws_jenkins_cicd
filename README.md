##FastAPI Payment Service   Jenkins CI/CD on AWS EC2

## Core Objective

This project automates the **end-to-end deployment pipeline** for a microservice:
Build the FastAPI app into a **Docker image**  
 Automatically deploy to **EC2 via Jenkins**  
 Run **pytest validation** before deployment  
 Monitor instance health using **CloudWatch metrics**  
 Triggerif CPU utilization > 80%  

#Overview

This project demonstrates a complete DevOps CI/CD pipeline for deploying a FastAPI-based Payment Service using Jenkins, Docker, and AWS EC2, integrated with AWS CloudWatch monitoring  and SNS alerting.

The objective was to automate build, test, and deployment stages for a Python microservice while learning essential DevOps concepts such as containerization, continuous delivery, and observability.
#Tech Stack

 Component                      Technology 
 Backend Framework             FastAPI (Python) 
 Containerization              Docker 
 CI/CD Tool                    Jenkins Pipeline 
 Cloud Platform                AWS EC2 
 Monitoring                    AWS CloudWatch 
 Version Control               Git & GitHub 

#Repository Structure

├── app/
│ └── main.py # FastAPI app (root and health endpoints)
├── tests/
│ └── test_payment.py # Pytest API health check
├── Dockerfile # Container
├── docker-compose.yml # Optional local testing setup
└── Jenkinsfile # CI/CD pipeline 

# Architecture Flow

Developer Push → GitHub Repo
↓
Jenkins (on EC2) → Pull Code → Build Docker Image
↓
Stop Old Container → Deploy New Container
↓
Health Check → Notify Success/Failure
↓
AWS CloudWatch → Monitors CPU/Network.

#python env 
<img width="960" height="504" alt="image 1 execting env and installing packages" src="https://github.com/user-attachments/assets/220231d3-df84-4009-ad97-91c743de8abb" />

#FastAPi (intially taken port no 8080 then changed the port to 8081)
<img width="960" height="504" alt="image 2 " src="https://github.com/user-attachments/assets/e2e45c7f-2df7-4c4d-9507-834953cc28b6" />

#Swager UI 
<img width="1366" height="720" alt="Screenshot 2025-10-19 180307" src="https://github.com/user-attachments/assets/1b8777fd-01f4-4239-9695-71ecd0ad2c18" />
<img width="960" height="504" alt="image 4 " src="https://github.com/user-attachments/assets/30032acd-0388-40dd-b26c-7ea370d0ccd4" />
<img width="960" height="504" alt="image 5 " src="https://github.com/user-attachments/assets/b60f1ac3-796c-4bb7-9495-6a0229b165e4" />

##Transactions (CRUD opertaions )
<img width="960" height="504" alt="image 6" src="https://github.com/user-attachments/assets/d8365933-a04e-4e7d-a430-0605a61eec0e" />

#pytests

pytest stage to verify that the deployed FastAPI service worked correctly before moving to the deploy phase.
The FastAPI app runs properly.
The endpoints (like /health) respond with HTTP 200 OK.
The response body matches what’s expected (e.g., {"status": "ok"}).
this is for In a CI/CD pipeline, this testing step is the safety gate between "build" and "deploy."

If any pytest fails:Jenkins marks the build as ❌ failed,
Deployment stops automatically,

we can prevent broken containers from going live.
<img width="960" height="504" alt="image 7" src="https://github.com/user-attachments/assets/14ff467c-aedf-4488-9669-cd995cb6cbdc" />
<img width="960" height="504" alt="image 8" src="https://github.com/user-attachments/assets/a3e94087-71d3-437a-8eb9-9c34ed74b76a" />

##install docker and jenkins (need java to run jenkins )
<img width="960" height="504" alt="installing java " src="https://github.com/user-attachments/assets/63c727ee-19f5-4afe-9178-1c61cd0654b7" />
<img width="1366" height="720" alt="Screenshot 2025-10-19 180208" src="https://github.com/user-attachments/assets/44507cff-0fb9-4c5d-9103-9876ff02e02d" />
![Uploading installing docker.png…]()


##docker build
<img width="960" height="504" alt="enable docker" src="https://github.com/user-attachments/assets/962cc614-55ef-4a67-9769-5f4028b32721" />

#got a port issue ads jenkins run on 8080 intally we have binded this for Fastapi now allocating them again 
<img width="1366" height="720" alt="Screenshot 2025-10-19 180208" src="https://github.com/user-attachments/assets/fb18532a-faec-4024-a6d1-c31c1f4cfad7" />
<img width="960" height="504" alt="logs of fast api " src="https://github.com/user-attachments/assets/a8f0da7d-313d-4787-9594-a5a62702e510" />

#jenkins
<img width="960" height="504" alt="jenkins pic" src="https://github.com/user-attachments/assets/8f18bc90-a00c-49bb-a937-185a59706eba" />
<img width="488" height="208" alt="Screenshot 2025-10-19 182025" src="https://github.com/user-attachments/assets/9a929550-02a4-4428-9295-15b013abebef" />
<img width="376" height="629" alt="Screenshot 2025-10-19 182412" src="https://github.com/user-attachments/assets/7870c5ff-5628-4288-9bba-b49bfd6530c7" />

commited jenkins file from ec2 to github
<img width="1366" height="720" alt="Screenshot 2025-10-19 183038" src="https://github.com/user-attachments/assets/9cea9319-0030-48f9-bf12-30b7f36632dd" />
configured jenkins thorugh elastic ip 
<img width="960" height="504" alt="jenkins port config" src="https://github.com/user-attachments/assets/fc1ef629-7bf5-438a-8aee-023471be2d3d" />

#adding jnekins as a groupuser
<img width="1920" height="1008" alt="jenkins script console verfifcation " src="https://github.com/user-attachments/assets/293bf8ec-897e-42b1-a35b-4e1993b96d8c" />


| Stage                  | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| **Checkout**           | Pulls latest code from GitHub              |
| **Build Docker Image** | Packages the FastAPI app                   |
| **Run Tests**          | Validates API using pytest                 |
| **Deploy Container**   | Runs container on EC2                      |
| **Health Check**       | Verifies app status via `/health` endpoint |

<img width="1366" height="720" alt="Screenshot 2025-10-19 193216" src="https://github.com/user-attachments/assets/ec465835-e1f8-4a79-9306-50d419e61715" />

Enable EC2 Metrics

Open CloudWatch → Metrics → EC2 → Per-instance metrics

Enable: CPUUtilization,NetworkIn / NetworkOut,StatusCheckFailed

Metric: CPUUtilization

Condition: > 80% for 5 minutes

<img width="1366" height="768" alt="Screenshot 2025-10-21 191951" src="https://github.com/user-attachments/assets/720dcd13-fb77-46b0-9417-42cbd95eba4f" />
<img width="1366" height="720" alt="Screenshot 2025-10-21 191723" src="https://github.com/user-attachments/assets/aeb64a7f-ba88-4797-a378-c84e853cd940" />
<img width="1366" height="720" alt="Screenshot 2025-10-21 194413" src="https://github.com/user-attachments/assets/07cb889e-c598-4621-a673-de2ee6f4b51a" />
<img width="1366" height="720" alt="Screenshot 2025-10-21 194707" src="https://github.com/user-attachments/assets/e11bbe2d-5063-46c3-bd75-bc5c82f5cbd9" />

## Author
**Yusuf Shaik**  
DevOps Engineer | AWS | Jenkins | Docker | Python  

 **skyusuf@gmail.com**  
 [LinkedIn](https://linkedin.com/in/yusufshaik19)  
[GitHub](https://github.com/Yusufshaik19)


