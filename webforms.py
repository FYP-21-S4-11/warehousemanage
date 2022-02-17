from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    IntegerField, DateField,SelectField
from wtforms.validators import DataRequired, NumberRange


# Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()], render_kw={"placeholder": "Enter Username"})
    password = PasswordField("Password:", validators=[DataRequired()], render_kw={"placeholder": "Enter Password"})
    type = SelectField("Log In As:", render_kw={"placeholder": "Enter User Type"}, choices=["Supplier", "Admin", "Staff"])

# ==================================
# Stock Add Form
class StockAddForm(FlaskForm):
    sku = StringField("Product SKU:", validators=[DataRequired()], render_kw={"placeholder": "Enter Product SKU..."})
    name = StringField("Product Name:", validators=[DataRequired()], render_kw={"placeholder": "Enter Product Name..."})
    description = StringField("Description:", validators=[DataRequired()], render_kw={"placeholder": "Enter Description..."})
    producttype = StringField("Product Type:", validators=[DataRequired()], render_kw={"placeholder": "Enter Product Type..."})

# ==================================
# Supplier Add Form
class SupplierAddForm(FlaskForm):
    code = StringField("Supplier Code:", validators=[DataRequired()], render_kw={"placeholder": "Enter Supplier Code..."})
    name = StringField("Supplier Name:", validators=[DataRequired()], render_kw={"placeholder": "Enter Supplier Name..."})
    password = StringField("Supplier Password:", validators=[DataRequired()], render_kw={"placeholder": "Enter Supplier Password..."})
    phone = StringField("Supplier Phone:", validators=[DataRequired()], render_kw={"placeholder": "Enter Supplier Phone..."})
    address = StringField("Supplier Address:", validators=[DataRequired()], render_kw={"placeholder": "Enter Supplier Address..."})
# ==================================
# Store Add Form
class StoreAddForm(FlaskForm):
    name = StringField("Store Name:", validators=[DataRequired()], render_kw={"placeholder": "Enter Store Name..."})
    code = StringField("Store Code:", validators=[DataRequired()], render_kw={"placeholder": "Enter Store Code..."})
    location = StringField("Location:" , validators=[DataRequired()], render_kw={"placeholder": "Enter Location..."})
    address = StringField("Address:", validators=[DataRequired()], render_kw={"placeholder": "Enter Address..."})

# Store Update Form
class StoreUpdateForm(FlaskForm):
    code = StringField("Store Code:", validators=[DataRequired()], render_kw={"placeholder": "Enter Store Code..."})
    location = StringField("Location:" , validators=[DataRequired()], render_kw={"placeholder": "Enter Location..."})
    address = StringField("Address:", validators=[DataRequired()], render_kw={"placeholder": "Enter Address..."})
    name = StringField("Store Name:", validators=[DataRequired()], render_kw={"placeholder": "Enter Store Name..."})

# ==================================
# Staff Add Form
class StaffAddForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()], render_kw={"placeholder": "Enter Name..."})
    username = StringField("Username:", validators=[DataRequired()], render_kw={"placeholder": "Enter Username..."})
    password = StringField("Staff Password:", validators=[DataRequired()], render_kw={"placeholder": "Enter Password..."})
    phone = StringField("Staff Phone:", validators=[DataRequired()], render_kw={"placeholder": "Enter Phone..."})
    address = StringField("Staff Address:", validators=[DataRequired()], render_kw={"placeholder": "Enter Address..."})
    email = StringField("Staff Email:", validators=[DataRequired()], render_kw={"placeholder": "Enter Email..."})

# ==================================
# Product Add Form
class ProductAddForm(FlaskForm):
    name = StringField("Product Name:", validators=[DataRequired()], render_kw={"placeholder": "Enter Product Name..."})
    type = SelectField("Product Type:", validators=[DataRequired()], choices=["heels", "runners", "socks", "sneakers", "socks", "wedges", "sandals", "clogs", "flats", "boots"])
    color = SelectField("Colour:", validators=[DataRequired()], choices=["red", "orange", "yellow", "green", "blue", "violet", "black", "white"])
    size = SelectField("Size:", validators=[DataRequired()], choices=["XS", "S", "M", "L", "XL", "3", "4", "5", "6", "7", "8", "9", "10", "11"])

# ===================================================

class TopicForm(FlaskForm):
	topic = StringField("Topic", validators=[DataRequired()], render_kw={"placeholder": "Enter Topic..."})
# ==================================
class ReportSelectForm(FlaskForm):
	start = DateField("Start Date:", validators=[DataRequired()])
	end = DateField("End Date:", validators=[DataRequired()])


class QuantityForRemove(FlaskForm):
    quantity = IntegerField("Quantity:", validators=[DataRequired(), NumberRange(min=1, max=999999)],render_kw={"placeholder": "Enter Quantity..."})
# ==================================
# BooleanField
	# DateField
	# DateTimeField
	# DecimalField
	# FileField
	# HiddenField
	# MultipleField
	# FieldList
	# FloatField
	# FormField
	# IntegerField
	# PasswordField
	# RadioField
	# SelectField
	# SelectMultipleField
	# SubmitField
	# StringField
	# TextAreaField

	## Validators
	# DataRequired
	# Email
	# EqualTo
	# InputRequired
	# IPAddress
	# Length
	# MacAddress
	# NumberRange
	# Optional
	# Regexp
	# URL
	# UUID
	# AnyOf
	# NoneOf

