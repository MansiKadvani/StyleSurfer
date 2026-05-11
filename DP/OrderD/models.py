from django.db import models
from DP.models import DPData
from Customer.Order.models import Order

######################################################################################
######################################################################################

class DPOrder(models.Model):
    dp = models.ForeignKey(DPData, on_delete=models.CASCADE, related_name='assigned_orders')
    order = models.OneToOneField(Order, on_delete=models.CASCADE)  # Ensure unique order per DP
    assigned_date = models.DateField(auto_now_add=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.order.order_id} → DP {self.dp.Dname} ({self.status})"

######################################################################################
######################################################################################
