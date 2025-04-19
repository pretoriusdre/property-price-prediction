# 🏡 property-price-prediction

Predict property prices using linear regression trained on similar past sales.

This tool helps you estimate property prices based on features such as number of bedrooms, bathrooms, car spaces, land size, and an optional **desirability score** for subjective factors. You can make predictions for current or **future dates**, taking market direction into account.

---

## 📦 Installation

1. **Install [Poetry](https://python-poetry.org/docs/)**  
   Poetry is used for dependency management and packaging.

2. **Install dependencies**  
   In the project root directory, run:

   ```bash
   poetry install
   ```
    You can use another tool such as pip to install the dependencies listed in pyproject.toml
---

## 📁 Data Preparation

Fill out your sales data in:

```
data/similar_sales.xlsx
```
![alt text](image.png)

Each row should represent a past sale and include the following columns:

- `data_model` – e.g. the suburb or zone name. This is used to segregate the data into independent models.
- `bed` – number of bedrooms  
- `bath` – number of bathrooms  
- `car` – number of car spaces  
- `land` – land size in square meters  
- `price` – final sale price  
- `date` – sale date in `YYYY-MM-DD` format  
- `desirability` – *(optional)* subjective score from 1–10 which accounts for intangible qualities like the building condition, street, etc. Set to a constant number eg 7 if you don't want to score.
- `url` – *(optional)* A link to the datasource
- `comments` – *(optional)* Notes about the property


---

## 📊 Making Predictions

You can run predictions via the included Jupyter Notebook:

```
interface.ipynb
```


### Sample prediction input:

```python
predictor.predict(
    {
        'data_model': 'suburb1',
        'bed': 3,
        'bath': 2,
        'car': 2,
        'land': 750,
        'desirability': 8,
        'date': '2025-04-20'
    }
)
```

_Predicted price for the house with parameters {'data_model': 'suburb1', 'bed': 3, 'bath': 2, 'car': 2, 'land': 750, 'desirability': 8, 'date': '2025-04-20'}:
$1,174,627_


---


### Contibuting:
If you want to contribute improvements to this, please raise a PR.