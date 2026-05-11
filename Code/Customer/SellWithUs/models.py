from django.db import models

######################################################################################
######################################################################################

class CustomerSellerReq(models.Model):
    csname = models.CharField(max_length=255)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    addr = models.TextField()
    boutique = models.CharField(max_length=255 , default="StyleSurfer")
    pincode = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    image_front = models.ImageField(upload_to='seller_requests/')
    image_back = models.ImageField(upload_to='seller_requests/')
    image_side = models.ImageField(upload_to='seller_requests/')# Store as comma-separated values
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected') , ('Verified', 'Verified')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

######################################################################################

class Customersell_SizeQuantity(models.Model):
    product = models.ForeignKey(CustomerSellerReq, on_delete=models.CASCADE, related_name='CustomerSellerReq_size_quantities')
    size = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.size}: {self.quantity}"

######################################################################################

class CustomerSellerProduct(models.Model):
    prod_type = models.CharField(max_length=255, default="sell_with_us")
    csname = models.CharField(max_length=255, default="abc")
    email = models.EmailField(default="stylesurfer3@gmail.com")
    number = models.CharField(max_length=15, default="1234567890")
    addr = models.TextField(default="by default")
    pincode = models.CharField(max_length=10, default="123456")
    boutique = models.CharField(max_length=255, default="StyleSurfer")
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    image_front = models.ImageField(upload_to='seller_reviews/')
    image_back = models.ImageField(upload_to='seller_reviews/')
    image_side = models.ImageField(upload_to='seller_reviews/')
    status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='inactive'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

######################################################################################

class Customerproduct_SizeQuantity(models.Model):
    product = models.ForeignKey(CustomerSellerProduct, on_delete=models.CASCADE, related_name='CustomerSellerProduct_size_quantities')
    size = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.size}: {self.quantity}"
    
######################################################################################
######################################################################################