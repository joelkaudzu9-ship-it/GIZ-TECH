# app/utils/analytics.py
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import Product, Message, Activity
from app.extensions import db


class Analytics:
    """Analytics utilities for dashboard"""

    @staticmethod
    def get_total_revenue():
        """Calculate total revenue from sold products"""
        sold_products = Product.query.filter_by(is_sold=True).all()
        return sum(p.price for p in sold_products)

    @staticmethod
    def get_total_views():
        """Get total product views"""
        return db.session.query(func.sum(Product.views)).scalar() or 0

    @staticmethod
    def get_sold_count():
        """Get number of sold products"""
        return Product.query.filter_by(is_sold=True).count()

    @staticmethod
    def get_message_count(read=None):
        """Get message count (optionally filter by read status)"""
        query = Message.query
        if read is not None:
            query = query.filter_by(is_read=read)
        return query.count()



    @staticmethod
    def get_recent_activity(limit=10):
        """Get recent activity for dashboard"""
        from app.models import Activity

        activities = Activity.query.order_by(
            Activity.created_at.desc()
        ).limit(limit).all()


        return activities

    @staticmethod
    def get_sales_trend(days=30):
        """Get sales trend data for charts"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # This is a placeholder - implement based on your data structure
        # You might need to track when products were sold
        return {
            'labels': [(start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                       for i in range(days)],
            'data': [0] * days  # Populate with actual sales data
        }

    @staticmethod
    def get_popular_products(limit=5):
        """Get most viewed products"""
        products = Product.query.order_by(
            Product.views.desc()
        ).limit(limit).all()

        return [{
            'title': p.title,
            'views': p.views,
            'messages': p.messages.count(),
            'is_sold': p.is_sold
        } for p in products]

    @staticmethod
    def get_conversion_rate():
        """Calculate views to messages conversion rate"""
        total_views = Analytics.get_total_views()
        total_messages = Analytics.get_message_count()

        if total_views == 0:
            return 0

        return round((total_messages / total_views) * 100, 2)