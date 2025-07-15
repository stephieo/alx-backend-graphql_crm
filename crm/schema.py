import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Order, Product
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

# ==========
#  defining GraphQL types. these are analogous to the Django Model
# ============

class CustomerType(graphene.ObjectType):
    class Meta:
        model = Customer # defining which model  maps to this type
        fields = ("id","name", "email", "phone") # defining which field are available to be accessed of mutated

class ProductType(graphene.ObjectType):
    class Meta:
        model = Product # defining which model  maps to this type
        fields = ("id","name", "price", "stock") # defining which field are available to be accessed of mutated

class OrderType(graphene.ObjectType):
    class Meta:
        model = Order # defining which model  maps to this type
        fields = ("id","customer", "products", "order_date", "total_amount") # defining which field are available to be accessed of mutated


# =============
# Defining Inputs
# ==============  
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(reqiured=True)
    email = graphene.String(reqiured=True)
    phone = graphene.String(reqiured=False)

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False)
    
class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(default_value=None)

#  =============
#  Defining Mutations: api actions that affect the database
#  ==============
class CreateCustomer(graphene.Mutation):
    class Arguments:
        """defining the arguments needed for the mutation"""
        name = graphene.String(reqiured=True)
        email = graphene.String(reqiured=True)
        phone = graphene.String(reqiured=False)

    #defining the return fields for this mutation
    customer = graphene.Field(CustomerType)
    message = graphene.String()


    #defining the logic for the mutation. analogous to making a custom create classs in DRF
    @classmethod
    def mutate(cls, root, info, name, email, phone=None):
        # validating  email
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("this email is already in use")
        
        #validating phone format
        if phone:
            phone_pattern = r"^\+?\d{1,4}[-.\s]?\d{3}[-.\s]?\d{3,4}$"
            if not re.match(phone_pattern, phone):
                raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890.")
            
        #the create Customer in db
        with transaction.atomic():
            customer = Customer.objects.create(name=name, email=email, phone=phone or "")
        
        #returning the response: an object with some fields
        return CreateCustomer(customer=customer, message="Customer created successfuly")
    

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customer_list = CustomerInput(required=True)
    
    customers = graphene.List(CustomerType)
    creation_errors =graphene.List(String)
    message = "Bulk creation complete"


    @classmethod
    def mutate(cls, root, info, customer_list):
        created_customers = []
        errors = []

        with transaction.atomic():
            for index, customer in enumerate(customer_list):
                name = customer.name
                email = customer.email
                phone = customer.phone

                if Customer.objects.filter(email=email).exists():
                    # logging errors in the list instead of breaking the flow with a raised error
                    errors.append(f"Customer {index + 1}: this email '{email}' is already in use")
                    continue
        
                #validating phone format
                if phone:
                    phone_pattern = r"^\+?\d{1,4}[-.\s]?\d{3}[-.\s]?\d{3,4}$"
                    if not re.match(phone_pattern, phone):
                        errors.append(f"Customer {index + 1}: Invalid phone format. Use +1234567890 or 123-456-7890.")
                        continue
                    
                #the creation logic
                customer = Customer.objects.create(name=name, email=email, phone=phone or "")
                created_customers.append(customer)
            
        return BulkCreateCustomers(customer_list=created_customers,
                                   creation_errors=errors, message=message)


class CreateProduct(graphene.Mutation):
    class Arguments:
        product_data = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, info, root, product_data):
        if price <= 0:
            raise ValidationError("price  must be greater than 0")
        if stock < 0:
            raise ValidationError("stock cannot be negative")
        with transaction.atomic():
            product = Product.objects.create(name=name, price=price, stock=stock)
        message = "product successfully created" if product else "Error: product creation unsuccessful"

        return CreateProduct(product=product, message=message) 
        

class CreateOrder(graphene.Mutation):
    class Arguments:
        order_data = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    message= graphene.String()

    @classmethod
    def mutate(cls, info, root, order_data):
        # validate customer
        customer_id = order_data.customer_id
        product_ids = order_data.product_ids
        order_date = order_data.order_date or timezone.now()

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Customer does not exist")
        
        # validate  products
        if not product_ids:
            raise ValidationError("Order must have at least one product")
        product_list = []
        for index, product_id in enumerate(product_ids):
            try:
                product = Product.objects.filter(id=product_id)
            except:
                Product.DoesNotExist:
                raise ValidationError(f"Item {index+1}, {product_id}: Product does not exist")
            product_list.append(product)

        if len(product_list) < len(product_ids):
            raise ValidationError("Invalid products in order")
        
        total_amount = sum(product.price for product in product_list)

        with transaction.atomic():
            order = Order.objects.create(
                customer=customer_id,
                products=product_list,
                total_amount=total_amount
                order_date=order_date
                )
        return CreateOrder(order=order, message="Order created successfully")


# ==============
# Main Mutation class.
# =================

class Mutation(graphene.ObjectType):
    """  this is where you sort of 'register' 
        the mutations you have defined with the keywords
        that will be used in the frontend
    """
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


