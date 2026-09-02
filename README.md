# RigBuilder

RigBuilder is a Machine Learning-based web application that helps users build a PC according to their budget and requirements.

The system uses a trained Machine Learning model to recommend suitable PC configurations based on user preferences.

🌐 **Live Demo:** https://rigbuilder.onrender.com

<br>

## Features

- User Signup and Login system
- Machine Learning-based PC build recommendation
- Budget-based PC recommendations
- Component selection and recommendation
- Save recommended PC builds to cart
- Remove saved PC builds
- Place order functionality
- CatBoost Machine Learning model integration
- PC component datasets
- Fully deployed web application

<br>

## Machine Learning

RigBuilder uses a Machine Learning model to generate PC build recommendations.

### Model Used

- CatBoost Classifier

The model helps recommend suitable PC configurations based on user input and preferences.

<br>

## Technologies Used

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Gunicorn

### Machine Learning

- Scikit-learn
- CatBoost
- Pandas
- NumPy
- Joblib

### Frontend

- HTML
- CSS
- Jinja2 Templates

### Database

- SQLite

### Deployment

- GitHub
- Render
- Hugging Face

<br>

## 📂 Project Structure

```text
RigBuilder/
├── app.py
├── requirements.txt
├── README.md
├── dataset/
├── models/
├── templates/
└── static/
```

<br>

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mohammedjunaidkhan00/RigBuilder.git
```

### 2. Move into the project directory

```bash
cd RigBuilder
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

<br>

## Machine Learning Model Storage

The trained ML model is stored separately using Hugging Face because large model files exceed GitHub's normal file size limits.

The application downloads the required model when it starts.

<br>

## Deployment

The application is deployed using Render.

**Live Application:** https://rigbuilder.onrender.com

<br>

## Future Improvements

- Support for more PC usage scenarios
- More component options
- Better hardware compatibility checking
- Advanced filtering options
- Performance comparison between multiple builds
- User profile and saved build history
- Price updates from online retailers
- Improved recommendation accuracy

<br>

## Author

**Mohammed Junaid Khan**

<br>

## If You Like This Project

Give the repository a ⭐ on GitHub!
