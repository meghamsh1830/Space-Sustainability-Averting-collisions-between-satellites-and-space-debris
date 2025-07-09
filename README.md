# Space-Sustainability-Averting-collisions-between-satellites-and-space-debris
A full-stack web application for space sustainability that predicts potential satellite collisions using TLE data, SGP4 orbital models, and Gaussian Mixture Models. It features an interactive 3D visualization and a Flask API for real-time collision risk assessment.

🌍Project Overview :
This project is designed to support space sustainability by predicting and preventing potential collisions between active satellites and space debris. It combines satellite tracking, probabilistic modeling, and real-time visualization into a full-stack system.
At its core, the project integrates Python (Flask) for the backend, SGP4 for orbital propagation, and Gaussian Mixture Models (GMM) for collision probability estimation. The results are delivered through a responsive web interface built with HTML, CSS, JavaScript, Bootstrap, Three.js, and ArcGIS for geospatial 3D visualization.
The system allows users to:
•	Search for any satellite by NORAD ID
•	View its current orbital details
•	Predict the highest-risk collision event over the next 7 days
🎯 Objectives :
•	Enhance space situational awareness through real-time visualization of orbital assets and debris.
•	Predict satellite collisions using accurate physical models and statistical uncertainty.
•	Promote sustainable space operations by helping satellite operators avoid potential conjunctions.
•	Provide an educational and analytical tool for researchers, space agencies, and students to explore orbital interactions.
•	Enable decision support through APIs that deliver predictive collision risk data over time.


Architecture :

 

🔬 Methodology :
The project is built using a modular, data-driven approach integrating Python and JavaScript:
1. Data Acquisition
•	Fetch TLE data using authenticated API access from space-track.org.
•	Maintain a dataset of relevant NORAD IDs for active satellites and known debris.
•	Active satellites  NORAD ID information. Link
2. Orbit Propagation
•	Use the SGP4 (Simplified General Perturbations) model via python-sgp4 to convert TLE data into satellite position and velocity in the ECI (Earth-Centered Inertial) frame.
•	Propagate orbits over a 7-day prediction window.
3. Collision Prediction Engine
•	Model positional uncertainty using multivariate Gaussian distributions.
•	Generate Monte Carlo samples around predicted orbits.
•	Apply Gaussian Mixture Models (GMM) to evaluate the probability of collision between target and neighboring objects.
•	Identify the highest-risk encounter for each object.
4. API Integration (Flask Backend)
•	Flask API endpoint /satellite-collision-probability accepts a target NORAD ID and returns:
o	Predicted closest encounter
o	Relative speed and distance
o	Collision probability
o	Geolocation (lat/lon) of the predicted risk zone
5. Web Interface (Frontend)
•	Visualize all satellites and debris using Three.js and ArcGIS.
•	Implement interactive filtering by object type, country, and size.
•	Display collision prediction results dynamically based on user search.

Collision Prediction Web App :
•	Website Link - LYNX
•	Collision Prediction - Collision prediction - by LYNX

