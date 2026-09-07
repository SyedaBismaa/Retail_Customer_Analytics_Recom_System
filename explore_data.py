# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 13:21:00 2026

@author: syeda
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


#Customer.CSv
df=pd.read_csv(r"C:\Users\syeda\OneDrive\Desktop\Retail\raw_datasets\customers (1).csv")
print(df.columns)
print(df.shape)
print(df.isna().sum())
#Null Vals
#-age -gender - occupation , income , marital status , prefferde_channel 

print(df.dtypes)
print(df['Gender'].unique()) #['Male' 'Female' 'Other' nan (hist)  DONE
df["Gender"]=df['Gender'].fillna(df['Gender'].mode()[0])     
print(df['City'].unique()) #--drop (multico)
print(df['State'].unique())

print(df['Customer_Since'].unique()) #_DateFeature (YY-DD-MM)     DONE
df['Customer_Since']=pd.to_datetime(df["Customer_Since"])
df["Year"] = df["Customer_Since"].dt.year
df["Month"] = df["Customer_Since"].dt.month
df["Day"] = df["Customer_Since"].dt.day

print(df["Occupation"].unique()) #-Onehot plus nullvalTreat (hist) ONEHOT(DONE)
print(df['Marital_Status'].unique()) #['Married' 'Single' 'Widowed' 'Divorced' nan] DONE
df["Marital_Status"]=df["Marital_Status"].fillna(df["Marital_Status"].mode()[0])
print(df['Preferred_Channel'].unique()) #['Online' 'Store' 'Mobile App' nan] hist  DONE
df["Preferred_Channel"]=df["Preferred_Channel"].fillna(df["Preferred_Channel"].mode()[0])
print(df['Loyalty_Tier'].unique()) #['Silver' 'Gold' 'Bronze' 'Platinum'] 
print(df['Age'].describe())
df["Age"]=df["Age"].fillna(df["Age"].median())
print(df["Income"].describe())
print(df['Income'].skew())
df['Income'] = df['Income'].fillna(df['Income'].median())
df=pd.get_dummies(df,columns=['Loyalty_Tier','Gender','Marital_Status','Preferred_Channel','Loyalty_Tier',
                              'State','Occupation'], dtype=int , drop_first=True )
#outliers   - age and income
df['Age'].hist(bins=50, edgecolor='black')
plt.xlabel('AGE')
plt.ylabel('Frequency')
plt.title('AGe Distribution')
plt.show()
df["Age_group"] = pd.cut(df['Age'],bins=[18,35,50,65,100],labels=['Young','Adult','Middle_Age','Old_Age'])
df['Income_bin'] = pd.qcut(df['Income'], q=4, labels=['Low','Medium','High','Very High'])
df=pd.get_dummies(df,columns=['Age_group','Income_bin'],dtype=int ,drop_first=True)









#Product CSV
df2=pd.read_csv(r"C:\Users\syeda\OneDrive\Desktop\Retail\raw_datasets\products (1).csv")

print(df2.shape)
print(df2.dtypes)
print(df2.isna().sum())

print(df2['Category'].unique())  #One
print(df2['Product_Name'].unique())  #leave
print(df2['Brand'].unique()) #One
print(df2['Subcategory'].unique())

df2=pd.get_dummies(df2,columns=['Category','Brand','Subcategory'],dtype=int, drop_first=True)

print(df2['Product_Rating'].describe())
df2['Discount'].fillna(df2['Discount'].median(), inplace=True)
df2['Stock_Quantity'].fillna(df2['Stock_Quantity'].median(), inplace=True)


#Order CSV
df3=pd.read_csv(r"C:\Users\syeda\OneDrive\Desktop\Retail\raw_datasets\orders.csv")
print(df3.shape)
print(df3.columns)
print(df3.dtypes)
print(df3.isna().sum())


df3["Order_Date"]=pd.to_datetime(df3["Order_Date"])
df3["Order_day"]=df3["Order_Date"].dt.day
df3["Order_Month"]=df3["Order_Date"].dt.month
df3["Order_Year"]=df3["Order_Date"].dt.year

print(df3["Order_Status"].unique()) #['Delivered' nan 'Pending' 'Cancelled' 'Returned']
df3["Order_Status"]=df3["Order_Status"].fillna(df3["Order_Status"].mode()[0])
print(df3["Sales_Channel"].unique()) #['Online' 'Store' 'Mobile App']
print(df3["Payment_Method"].unique()) #['Cash on Delivery' 'UPI' 'Net Banking' 'Debit Card' 'Credit Card' nan]
df3["Payment_Method"]=df3["Payment_Method"].fillna(df3["Payment_Method"].mode()[0])
print(df3["Shipping_City"].unique()) #33 including nan ignore will better
print(df3["Shipping_State"].unique()) #16 includeing nan
df3["Shipping_State"]=df3["Shipping_State"].fillna(df3["Shipping_State"].mode()[0])

df3=pd.get_dummies(df3,columns=["Order_Status","Sales_Channel","Payment_Method","Shipping_State"],dtype=int, drop_first=True)



#Order Items (Checks)
df4=pd.read_csv(r"C:\Users\syeda\OneDrive\Desktop\Retail\raw_datasets\order_items.csv")
print(df4.shape)
print(df4.columns)
print(df4.dtypes)
print(df4.isna().sum())
print(df4["Order_Item_ID"].duplicated().sum())
print(df4["Quantity"].describe())
print(df4["Discount"].describe())
print((df4["Item_Total"] - 
       (df4["Quantity"] * df4["Unit_Price"] * (1 - df4["Discount"]/100))).abs().describe())






# Create folder
cleaned_path = r"C:\Users\syeda\OneDrive\Desktop\Retail\cleaned_datasets"
os.makedirs(cleaned_path, exist_ok=True)

df.to_csv(os.path.join(cleaned_path, "customers_clean.csv"), index=False)
df2.to_csv(os.path.join(cleaned_path, "products_clean.csv"), index=False)
df3.to_csv(os.path.join(cleaned_path, "orders_clean.csv"), index=False)
df4.to_csv(os.path.join(cleaned_path, "order_items_clean.csv"), index=False)

