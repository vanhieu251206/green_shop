@admin.register(Order)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'phone', 'status', 'total_price', 'created_at']
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone')
    inlines = [OrderItemInline]