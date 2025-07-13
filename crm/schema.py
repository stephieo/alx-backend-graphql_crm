import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Order, Product
from django.core.exceptions import ValidationError

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query)

# defining GraphQL types. these are analogous to the Django Model
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
            
        #the creation logic
        customer = Customer.objects.create(name=name, email=email, phone=phone or "")
        return CreateCustomer(customer=customer, message="Customer created successfuly")