# dgi-portfolio-tracker

A dividend growth portfolio tracker program that allows you to trace the movements of your individual holdings and get key metrics.
A portfolio simulation sheet can be generated as well based on last years metrics.   


## Getting Started
### Prerequisites
- Python 3.7 or greater with PIP package manager
- git on path

### Installation

Clone project to local directory:
```
c:\temp> git clone git@github.com:nissant/dgi-portfolio-tracker.git
```
Install Project Requirements
```
c:\temp\dgi-portfolio-tracker> pip install -r requirements.txt
```

## Usage
### Generating Portfolio From Transactions
Create portfolio transactions table in xlsx format (Can be exported from stock brocker or bank website).
- Transaction table labels must include:

| Date     | Symbol  | Qty  | Side  | Price  | Principal  | Comm  |
|----------|---------|------|-------|--------|------------|-------|
|   8/7/19 | CAT     | 30   |Buy    | 134.5  | 4035       | 5     |
### Run Script
```
c:\temp\dgi-portfolio-tracker> python main.py <path_to_transaction_table.xlsx> <out_directory_path>
```

## Contributing

Please read [CONTRIBUTING.md]() for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Nisan Tagar* - *Initial work* - [Nissant](https://github.com/nissant)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

