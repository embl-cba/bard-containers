# BARD Containers

This repository contains the container recipes for the BARD virtual desktop. BARD is built on top of the the open-source project [abcdesktop](https://www.abcdesktop.io/).
## Current deployment of BARD

 - EMBL Heidelberg
   
Public instance: https://bard-external.embl.de

Internal instance:   https://bard.embl.de

To request a demo or testing account, please send an email to itsupport@embl.de

## Courses that used BARD
|Name|No. of Participants  |Location| Dates|
|--|--|--|--|
| Advanced deep learning for image analysis |24  | Germany| Feb 2025|
|EMBO Practical, Integrative structural biology: solving molecular puzzles| 20|Germany|Oct.2024|
|EMBL Pre-doc course| 14|Germany|Oct.2024|
| EMBO Practical, Current methods in cell biology |24  | Germany| September 2024|
| EMBO Advances in cryo-electron microscopy and 3D image processing |30  | Germany, Virtual| Aug 2024|


## Files

### System containers
The system containers in this repository (listed below) are specific to EMBL instances. However, they can be adapted for use in other environments with the necessary modifications.

### Application containers
Each folder contains:
-   A **container recipe** (a standard Docker recipe with BARD-specific configurations)
-   A **JSON file** (generated by running `docker inspect`, used for deployment to BARD)
-   A **logo image** in `.svg` format (representing the application’s logo, converted to a base64 string named `icondata` in the container recipe)


## Container Descriptions
### System containers
|Container Name|Description  |
|--|--|
|cleanup |container used as k8s cron job to automatically remove pods older than 48hrs|
|oc.nginx.external | front end web container for EMBL external BARD instance |
|oc.nginx| same as oc.nginx.external, but it is used for the EMBL internal instance|
|oc.user.embl| container which include basic software, dependencies for user pod |
|oc.user.external| same as oc..user.embl but it is used for the EMBL external instance |
|pyos | main controller container for the BARD desktop|

### Application containers
Application containers are standard docker containers with BARD specific features(for example , additional `LABEL`)
- The `LABEL` are required for the application to appear in BARD desktop.
- The base-images recipes contain dependencies such as X11 etc which are essential for BARD.  It is recommended to start building your own application container from base-images.
- .json file is used for deployment of the application.  After building docker container, the .json file can be created with `docker inspect CONTAINER_ID`
- BARD requires icons in SVG format. You can encode your `.svg` logo into Base64 by running:  
`bash base64 example.svg ` Then, copy the resulting string into the `LABEL oc.icondata` field within the container recipe.
- The last few lines in container recipe,(e.g. those handling `localaccount, passwd`) are required by BARD, so that the containerized application runs under the current logged in user.

## Deploy containers to BARD
1. To deploy the apps to your own instance, it follows the same procedure as the [abcdesktop](abcdesktop.io) For example,
`curl -X PUT -H 'Content-type: text/javascript' https://YOUR_BARD_INSTANCE/API/manager/image -d@fiji.json`
where replace fiji.json with the correct json file.
2. To request new apps, please open a PR in this repository




# Citation
If you find BARD useful, and used it for your research, please cite the below.

> Tischer, C., Hériché, J.-K., & Sun, Y. (2025). A Virtual Bioimage Analysis Research Desktop (BARD) for Deployment of Bioimage Tools on Kubernetes. Base4NFDI User Conference 2024 (UC4B2024), Berlin. Zenodo. https://doi.org/10.5281/zenodo.14643885



