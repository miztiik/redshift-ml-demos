# Airflow Demo

Can you help help the engineers at Mystique Unicorn to deploy a churn prediction model in Redshift using the new Redshift ML feature<sup>[1]</sup>?

## 🎯 Solutions

1. Create a Multi-AZ VPC with NAT Gateway
1. Create Redshift cluster environment will be configured to have a public endpoint and secrets stored in secrets manager<sup>[2]</sup>
1. Connect to the cluster using query editor in redshift console
1. Let us do the `churn prediction` example shown in this doc<sup>[3]</sup>
1. Check model state,

```sql
select schema_name, model_name, model_state from stv_ml_model_info;

 schema_name |        model_name         |  model_state
-------------+---------------------------+----------------
 public      | customer_churn_auto_model | Model is Ready

```
1. Predict proportion of churners and non-churners among customers from different states from `2020-01-01`

```sql
WITH inferred AS (SELECT state,
       customer_churn_auto_model( 
          state,
          account_length,
          area_code, 
          total_charge/account_length, 
          cust_serv_calls/account_length )::varchar(6)
          AS active FROM customer_activity
          WHERE record_date > '2020-01-01' )
SELECT state, SUM(CASE WHEN active = 'True.' THEN 1 ELSE 0 END) AS churners,
       SUM(CASE WHEN active = 'False.' THEN 1 ELSE 0 END) AS nonchurners,
       COUNT(*) AS total_per_state
FROM inferred
GROUP BY state
ORDER BY state;
```


## 📌 Who is using this

This repository aims to show how to Redshift ML to new developers, Solution Architects & Ops Engineers in AWS. Based on that knowledge these Udemy [course #1][102], [course #2][101] helps you build complete architecture in AWS.

### 💡 Help/Suggestions or 🐛 Bugs

Thank you for your interest in contributing to our project. Whether it is a bug report, new feature, correction, or additional documentation or solutions, we greatly value feedback and contributions from our community. [Start here](/issues)

### 👋 Buy me a coffee

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q41QDGK) Buy me a [coffee ☕][900].

### 📚 References

1. [Docs: Getting started with Amazon Redshift ML][1]

1. [Docs: Getting started with Amazon Redshift][2]
1. [Docs: Getting started with Amazon Redshift ML Churn Prediction][3]

### 🏷️ Metadata

![miztiik-success-green](https://img.shields.io/badge/Miztiik:Automation:Level-300-purple)

**Level**: 300

[1]: https://docs.aws.amazon.com/redshift/latest/dg/geting-started-machine-learning.html
[2]: https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-prereq.html
[3]: https://docs.aws.amazon.com/redshift/latest/dg/examples.html

[100]: https://www.udemy.com/course/aws-cloud-security/?referralCode=B7F1B6C78B45ADAF77A9
[101]: https://www.udemy.com/course/aws-cloud-security-proactive-way/?referralCode=71DC542AD4481309A441
[102]: https://www.udemy.com/course/aws-cloud-development-kit-from-beginner-to-professional/?referralCode=E15D7FB64E417C547579
[103]: https://www.udemy.com/course/aws-cloudformation-basics?referralCode=93AD3B1530BC871093D6
[899]: https://www.udemy.com/user/n-kumar/
[900]: https://ko-fi.com/miztiik
[901]: https://ko-fi.com/Q5Q41QDGK