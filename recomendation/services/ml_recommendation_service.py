from typing import List, Dict, Any
import os
import logging
from datetime import datetime
import pickle
from collections import defaultdict

from models.schemas import ProductRecommendation
from services.database_manager import DatabaseManager

class MLRecommendationService:
    """
    Streamlined ML-powered recommendation service focusing on:
    1. Similar products (ML-based)  
    2. Co-purchase recommendations (what people bought together)
    3. Easy model training
    4. Data sync from production
    5. Health checks
    """
    def __init__(self, production_db_url: str, analytics_db_url: str, model_path: str = "models/"):
        self.production_db_url = production_db_url
        self.analytics_db_url = analytics_db_url
        self.model_path = model_path
        
        # Initialize database managers
        self.prod_db_manager = DatabaseManager(production_db_url)
        self.analytics_db_manager = DatabaseManager(analytics_db_url)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize model storage
        self.similarity_matrix = None
        self.copurchase_matrix = None
        self.product_features = {}
        self.models_trained = False
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        # Try to load existing models
        self._load_models()

    def _load_models(self):
        """Load trained models from disk"""
        try:
            similarity_path = os.path.join(self.model_path, "similarity_matrix.pkl")
            copurchase_path = os.path.join(self.model_path, "copurchase_matrix.pkl")
            features_path = os.path.join(self.model_path, "product_features.pkl")
            
            if all(os.path.exists(p) for p in [similarity_path, copurchase_path, features_path]):
                with open(similarity_path, 'rb') as f:
                    self.similarity_matrix = pickle.load(f)
                with open(copurchase_path, 'rb') as f:
                    self.copurchase_matrix = pickle.load(f)
                with open(features_path, 'rb') as f:
                    self.product_features = pickle.load(f)
                
                self.models_trained = True
                self.logger.info("ML models loaded successfully")
            else:
                self.logger.warning("No trained models found. Train models first.")
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
            self.models_trained = False

    def _save_models(self):
        """Save trained models to disk"""
        try:
            similarity_path = os.path.join(self.model_path, "similarity_matrix.pkl")
            copurchase_path = os.path.join(self.model_path, "copurchase_matrix.pkl")
            features_path = os.path.join(self.model_path, "product_features.pkl")
            
            with open(similarity_path, 'wb') as f:
                pickle.dump(self.similarity_matrix, f)
            with open(copurchase_path, 'wb') as f:
                pickle.dump(self.copurchase_matrix, f)
            with open(features_path, 'wb') as f:
                pickle.dump(self.product_features, f)
                
            self.logger.info("Models saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving models: {str(e)}")

    def sync_production_data(self) -> Dict[str, Any]:
        """
        Sync data from production database to analytics database for ML training
        """
        try:
            self.logger.info("Starting data sync from production to analytics...")
            
            # Get SQL dialect for creating tables
            dialect = self.analytics_db_manager.get_sql_dialect()
            
            # Create analytics tables if they don't exist using execute_script
            create_tables_sql = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    password VARCHAR(255),
                    role VARCHAR(50),
                    sort_option VARCHAR(50),
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS products (
                    id INT PRIMARY KEY,
                    name VARCHAR(255),
                    price DECIMAL(10,2),
                    brand VARCHAR(255),
                    category VARCHAR(255),
                    rating DECIMAL(3,2),
                    picture TEXT,
                    stock INT,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS orders (
                    id INT PRIMARY KEY,
                    customer_id INT,
                    total_amount DECIMAL(10,2),
                    created_at TIMESTAMP,
                    stripe_session_id VARCHAR(255),
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS orderitem (
                    id INT PRIMARY KEY,
                    order_id INT,
                    product_id INT,
                    quantity INT,
                    total_amount DECIMAL(10,2),
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            
            self.analytics_db_manager.execute_script(create_tables_sql)
            
            # Connect to both databases
            prod_conn = self.prod_db_manager.get_connection(timeout=30.0)
            analytics_conn = self.analytics_db_manager.get_connection(timeout=30.0)
            
            try:
                prod_cursor = prod_conn.cursor()
                analytics_cursor = analytics_conn.cursor()
                
                # Clear analytics data
                for table in ['users', 'products', 'orders', 'orderitem']:
                    analytics_cursor.execute(f"DELETE FROM {table}")
                
                # Sync users (simplified - just IDs and essential fields)
                prod_cursor.execute("SELECT id, name, email FROM users")
                users = prod_cursor.fetchall()
                for user in users:
                    analytics_cursor.execute(
                        "INSERT INTO users (id, name, email, password, role, sort_option) VALUES (%s, %s, %s, %s, %s, %s)",
                        (user['id'], user['name'], user['email'], 'synced', 'customer', None)
                    )
                
                # Sync products
                prod_cursor.execute("SELECT * FROM products")
                products = prod_cursor.fetchall()
                for product in products:
                    analytics_cursor.execute(
                        "INSERT INTO products (id, name, price, brand, category, rating, picture, stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (product['id'], product['name'], product['price'], product['brand'], 
                         product['category'], product['rating'], product['picture'], product['stock'])
                    )
                
                # Sync orders
                prod_cursor.execute("SELECT * FROM orders")
                orders = prod_cursor.fetchall()
                for order in orders:
                    analytics_cursor.execute(
                        "INSERT INTO orders (id, customer_id, total_amount, created_at) VALUES (%s, %s, %s, %s)",
                        (order['id'], order['customer_id'], order['total_amount'], order['created_at'])
                    )
                
                # Sync order items (from orderitem table)
                prod_cursor.execute("SELECT * FROM orderitem")
                order_items = prod_cursor.fetchall()
                for item in order_items:
                    analytics_cursor.execute(
                        "INSERT INTO orderitem (id, order_id, product_id, quantity, total_amount) VALUES (%s, %s, %s, %s, %s)",
                        (item['id'], item['order_id'], item['product_id'], item['quantity'], item['total_amount'])
                    )
                
                analytics_conn.commit()
                
                # Get sync statistics
                stats = {
                    "users_synced": len(users),
                    "products_synced": len(products),
                    "orders_synced": len(orders),
                    "order_items_synced": len(order_items),
                    "sync_timestamp": datetime.now().isoformat()
                }
                
                self.logger.info(f"Data sync completed: {stats}")
                return {"status": "success", "stats": stats}
                
            finally:
                prod_conn.close()
                analytics_conn.close()
            
        except Exception as e:
            self.logger.error(f"Data sync failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def train_models(self) -> Dict[str, Any]:
        """
        Train ML models for product recommendations
        """
        try:
            self.logger.info("Starting ML model training...")
            start_time = datetime.now()
            
            # Connect to analytics database
            conn = self.analytics_db_manager.get_connection()
            
            # Build co-purchase matrix (what people bought together)
            self.logger.info("Building co-purchase matrix...")
            self.copurchase_matrix = self._build_copurchase_matrix(conn)
            
            # Build product similarity matrix  
            self.logger.info("Building product similarity matrix...")
            self.similarity_matrix = self._build_similarity_matrix(conn)
            
            # Load product features
            self.logger.info("Loading product features...")
            self.product_features = self._load_product_features(conn)
            
            conn.close()
            
            # Save models
            self._save_models()
            self.models_trained = True
            
            end_time = datetime.now()
            training_time = (end_time - start_time).total_seconds()
            
            result = {
                "status": "success",
                "training_time_seconds": training_time,
                "products_count": len(self.product_features),
                "copurchase_pairs": len(self.copurchase_matrix),
                "similarity_pairs": len(self.similarity_matrix),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Model training completed in {training_time:.2f} seconds")
            return result
            
        except Exception as e:
            self.logger.error(f"Model training failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _build_copurchase_matrix(self, conn) -> Dict:
        """Build co-purchase matrix using neural collaborative filtering approach"""
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Create user-item interaction matrix for neural collaborative filtering
            user_item_matrix = self._build_user_item_matrix(conn)
            
            if user_item_matrix is None:
                return self._build_simple_copurchase_matrix(conn)
            
            # Apply matrix factorization (core of neural collaborative filtering)
            item_embeddings = self._matrix_factorization(user_item_matrix)
            
            # Calculate item-item similarity from embeddings
            copurchase = defaultdict(dict)
            
            # Get all unique product IDs
            product_query = "SELECT DISTINCT product_id FROM orderitem ORDER BY product_id"
            cursor = conn.cursor()
            cursor.execute(product_query)
            products = cursor.fetchall()
            product_ids = [p['product_id'] for p in products]
            
            # Calculate cosine similarity between item embeddings
            if len(item_embeddings) > 1:
                similarities = cosine_similarity(item_embeddings)
                
                for i, prod_id1 in enumerate(product_ids):
                    for j, prod_id2 in enumerate(product_ids):
                        if i != j and similarities[i][j] > 0.2:
                            # Convert similarity to frequency-like score
                            copurchase[prod_id1][prod_id2] = float(similarities[i][j] * 10)
            
            return dict(copurchase)
            
        except ImportError:
            return self._build_simple_copurchase_matrix(conn)

    def _build_user_item_matrix(self, conn):
        """Build user-item interaction matrix"""
        try:
            import numpy as np
            
            # Get user-item interactions
            query = """
            SELECT DISTINCT orders.customer_id, orderitem.product_id, 
                   SUM(orderitem.quantity) as interaction_strength
            FROM orders
            JOIN orderitem ON orders.id = orderitem.order_id
            GROUP BY orders.customer_id, orderitem.product_id
            """
            
            cursor = conn.cursor()
            cursor.execute(query)
            interactions = cursor.fetchall()
            
            if not interactions:
                return None
            
            # Create mappings
            user_ids = sorted(list(set([row['customer_id'] for row in interactions])))
            item_ids = sorted(list(set([row['product_id'] for row in interactions])))
            
            user_to_idx = {user_id: idx for idx, user_id in enumerate(user_ids)}
            item_to_idx = {item_id: idx for idx, item_id in enumerate(item_ids)}
            
            # Build matrix
            matrix = np.zeros((len(user_ids), len(item_ids)))
            
            for row in interactions:
                user_idx = user_to_idx[row['customer_id']]
                item_idx = item_to_idx[row['product_id']]
                matrix[user_idx][item_idx] = row['interaction_strength']
            
            return matrix
            
        except Exception as e:
            self.logger.error(f"Error building user-item matrix: {str(e)}")
            return None

    def _matrix_factorization(self, user_item_matrix, n_factors=10, n_iterations=100):
        """Simple matrix factorization (neural network concept)"""
        try:
            import numpy as np
            
            n_users, n_items = user_item_matrix.shape
            
            # Initialize embeddings (similar to neural network weight initialization)
            np.random.seed(42)
            user_embeddings = np.random.normal(0, 0.1, (n_users, n_factors))
            item_embeddings = np.random.normal(0, 0.1, (n_items, n_factors))
            
            # Simple gradient descent (neural network training concept)
            learning_rate = 0.01
            regularization = 0.01
            
            for iteration in range(n_iterations):
                for u in range(n_users):
                    for i in range(n_items):
                        if user_item_matrix[u][i] > 0:
                            # Prediction
                            prediction = np.dot(user_embeddings[u], item_embeddings[i])
                            error = user_item_matrix[u][i] - prediction
                            
                            # Gradient descent updates (neural network backpropagation concept)
                            user_embedding_update = learning_rate * (error * item_embeddings[i] - regularization * user_embeddings[u])
                            item_embedding_update = learning_rate * (error * user_embeddings[u] - regularization * item_embeddings[i])
                            
                            user_embeddings[u] += user_embedding_update
                            item_embeddings[i] += item_embedding_update
            
            return item_embeddings
            
        except Exception as e:
            self.logger.error(f"Error in matrix factorization: {str(e)}")
            return np.random.random((user_item_matrix.shape[1], 10))

    def _build_simple_copurchase_matrix(self, conn) -> Dict:
        """Fallback: Build simple frequency-based co-purchase matrix"""
        copurchase = defaultdict(lambda: defaultdict(int))
        
        # Find products bought together in same cart/order
        query = """
        SELECT o1.product_id as product1, o2.product_id as product2, COUNT(*) as frequency
        FROM orderitem o1
        JOIN orderitem o2 ON o1.order_id = o2.order_id AND o1.product_id < o2.product_id
        GROUP BY o1.product_id, o2.product_id
        HAVING frequency >= 2
        ORDER BY frequency DESC
        """
        
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            copurchase[row['product1']][row['product2']] = row['frequency']
            copurchase[row['product2']][row['product1']] = row['frequency']  # Make symmetric
        
        return dict(copurchase)

    def _build_similarity_matrix(self, conn) -> Dict:
        """Build product similarity matrix using neural network embeddings"""
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            from sklearn.preprocessing import StandardScaler
            from sklearn.decomposition import PCA
            
            similarity = defaultdict(dict)
            
            # Get all products with features
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, name, price, brand, category, rating
            FROM products
            """)
            products = cursor.fetchall()
            
            if len(products) < 2:
                return dict(similarity)
            
            # Create feature vectors for ML processing
            feature_vectors = []
            product_ids = []
            
            # Get unique categories and brands for encoding
            categories = list(set([p['category'] for p in products if p['category']]))
            brands = list(set([p['brand'] for p in products if p['brand']]))
            
            for product in products:
                # One-hot encode categorical features
                cat_vector = [1 if product['category'] == cat else 0 for cat in categories]
                brand_vector = [1 if product['brand'] == brand else 0 for brand in brands]
                
                # Normalize numerical features
                price = float(product['price']) if product['price'] else 0.0
                rating = float(product['rating']) if product['rating'] else 3.0
                
                # Combine all features into a vector
                feature_vector = cat_vector + brand_vector + [price, rating]
                feature_vectors.append(feature_vector)
                product_ids.append(product['id'])
            
            # Convert to numpy array for ML processing
            X = np.array(feature_vectors)
            
            # Standardize features (important for neural network-style processing)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply PCA for dimensionality reduction (neural network concept)
            pca = PCA(n_components=min(10, X_scaled.shape[1]))
            X_reduced = pca.fit_transform(X_scaled)
            
            # Calculate cosine similarity (used in neural collaborative filtering)
            similarity_scores = cosine_similarity(X_reduced)
            
            # Build similarity matrix
            for i, prod_id1 in enumerate(product_ids):
                for j, prod_id2 in enumerate(product_ids):
                    if i != j:
                        score = similarity_scores[i][j]
                        if score > 0.3:  # Only store significant similarities
                            similarity[prod_id1][prod_id2] = float(score)
            
            return dict(similarity)
            
        except ImportError:
            # Fallback to simple rule-based approach if ML libraries not available
            return self._build_simple_similarity_matrix(conn)

    def _build_simple_similarity_matrix(self, conn) -> Dict:
        """Fallback: Build simple rule-based similarity matrix"""
        similarity = defaultdict(dict)
        
        # Get all products with features
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, name, price, brand, category, rating
        FROM products
        """)
        products = cursor.fetchall()
        
        # Calculate similarity between products
        for i, prod1 in enumerate(products):
            for j, prod2 in enumerate(products[i+1:], i+1):
                sim_score = self._calculate_product_similarity(prod1, prod2)
                if sim_score > 0.3:  # Only store significant similarities
                    similarity[prod1['id']][prod2['id']] = sim_score
                    similarity[prod2['id']][prod1['id']] = sim_score
        
        return dict(similarity)

    def _calculate_product_similarity(self, prod1, prod2) -> float:
        """Calculate similarity score between two products"""
        score = 0.0
        
        # Category match (high weight)
        if prod1['category'] == prod2['category']:
            score += 0.4
        
        # Brand match (medium weight)  
        if prod1['brand'] == prod2['brand']:
            score += 0.3
        
        # Price similarity (low weight)
        if prod1['price'] and prod2['price']:
            price_diff = abs(prod1['price'] - prod2['price'])
            max_price = max(prod1['price'], prod2['price'])
            if max_price > 0:
                price_sim = 1 - (price_diff / max_price)
                score += price_sim * 0.2
        
        # Rating similarity (low weight)
        #if prod1['rating'] and prod2['rating']:
        #    rating_diff = abs(prod1['rating'] - prod2['rating'])
        #    rating_sim = 1 - (rating_diff / 5.0)  # Assuming 5-star rating
        #    score += rating_sim * 0.1
        
        return min(score, 1.0)

    def _load_product_features(self, conn) -> Dict:
        """Load all product features"""
        features = {}
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        
        for product in products:
            features[product['id']] = {
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'brand': product['brand'],
                'category': product['category'],
                'rating': product['rating'],
                'picture': product['picture'],
                'stock': product['stock']
            }
        
        return features

    def get_similar_products(self, product_id: int, limit: int = 10) -> List[ProductRecommendation]:
        """
        Get similar products based on ML similarity matrix
        """
        if not self.models_trained:
            return self._get_fallback_similar_products(product_id, limit)
        
        try:
            if product_id not in self.similarity_matrix:
                return self._get_fallback_similar_products(product_id, limit)
            
            # Get similar products sorted by similarity score
            similar = self.similarity_matrix[product_id]
            sorted_similar = sorted(similar.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            recommendations = []
            for similar_id, score in sorted_similar:
                if similar_id in self.product_features:
                    product = self.product_features[similar_id]
                    
                    recommendation = ProductRecommendation(
                        product_id=similar_id,
                        name=product['name'],
                        price=product['price'],
                        brand=product['brand'],
                        category=product['category'],
                        rating=product['rating'],
                        picture=product['picture'],
                        score=float(score),
                        reason=f"Similar to your selected product (ML similarity: {score:.2f})"
                    )
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in similar products: {str(e)}")
            return self._get_fallback_similar_products(product_id, limit)

    def get_copurchase_recommendations(self, product_id: int, limit: int = 10) -> List[ProductRecommendation]:
        """
        Get products frequently bought together with the given product
        """
        if not self.models_trained:
            return self._get_fallback_copurchase_recommendations(product_id, limit)
        
        try:
            if product_id not in self.copurchase_matrix:
                return self._get_fallback_copurchase_recommendations(product_id, limit)
            
            # Get co-purchased products sorted by frequency
            copurchased = self.copurchase_matrix[product_id]
            sorted_copurchased = sorted(copurchased.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            recommendations = []
            for copurch_id, frequency in sorted_copurchased:
                if copurch_id in self.product_features:
                    product = self.product_features[copurch_id]
                    
                    # Normalize frequency score (simple approach)
                    max_freq = max(copurchased.values()) if copurchased else 1
                    score = frequency / max_freq
                    
                    recommendation = ProductRecommendation(
                        product_id=copurch_id,
                        name=product['name'],
                        price=product['price'],
                        brand=product['brand'],
                        category=product['category'],
                        rating=product['rating'],
                        picture=product['picture'],
                        score=float(score),
                        reason=f"Frequently bought together ({frequency} times with others)"
                    )
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in co-purchase recommendations: {str(e)}")
            return self._get_fallback_copurchase_recommendations(product_id, limit)

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get system health status and model information
        """
        try:
            # Check model files
            model_files = {
                "similarity_matrix": os.path.exists(os.path.join(self.model_path, "similarity_matrix.pkl")),
                "copurchase_matrix": os.path.exists(os.path.join(self.model_path, "copurchase_matrix.pkl")),
                "product_features": os.path.exists(os.path.join(self.model_path, "product_features.pkl"))
            }
            
            # Check database connections
            db_status = {}
            try:
                conn = self.prod_db_manager.get_connection(timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                conn.close()
                db_status["production"] = "healthy"
            except Exception as e:
                db_status["production"] = f"error: {str(e)}"
            
            try:
                conn = self.analytics_db_manager.get_connection(timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                conn.close()
                db_status["analytics"] = "healthy"
            except Exception as e:
                db_status["analytics"] = f"error: {str(e)}"
            
            # Model statistics
            model_stats = {}
            if self.models_trained:
                model_stats = {
                    "products_count": len(self.product_features) if self.product_features else 0,
                    "similarity_pairs": sum(len(v) for v in self.similarity_matrix.values()) if self.similarity_matrix else 0,
                    "copurchase_pairs": sum(len(v) for v in self.copurchase_matrix.values()) if self.copurchase_matrix else 0
                }
            
            return {
                "status": "healthy" if self.models_trained and all(db_status.values()) else "degraded",
                "models_trained": self.models_trained,
                "model_files": model_files,
                "database_status": db_status,
                "model_statistics": model_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _get_fallback_similar_products(self, product_id: int, limit: int) -> List[ProductRecommendation]:
        """Fallback for similar products when ML model is not available"""
        try:
            conn = self.prod_db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get original product
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            original = cursor.fetchone()
            if not original:
                return []
            
            # Find products in same category
            query = """
            SELECT * FROM products 
            WHERE category = %s AND id != %s AND stock > 0
            ORDER BY rating DESC, price ASC
            LIMIT %s
            """
            
            cursor.execute(query, (original['category'], product_id, limit))
            results = cursor.fetchall()
            conn.close()
            
            recommendations = []
            for product in results:
                recommendation = ProductRecommendation(
                    product_id=product['id'],
                    name=product['name'],
                    price=product['price'],
                    brand=product['brand'],
                    category=product['category'],
                    rating=product['rating'],
                    picture=product['picture'],
                    score=0.6,
                    reason=f"Same category as {original['name']}"
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Fallback similar products error: {str(e)}")
            return []

    def _get_fallback_copurchase_recommendations(self, product_id: int, limit: int) -> List[ProductRecommendation]:
        """Fallback for co-purchase recommendations when ML model is not available"""
        try:
            conn = self.prod_db_manager.get_connection()
            cursor = conn.cursor()
            
            # Simple co-purchase query (using orderitem table structure)
            query = """
            SELECT p.*, COUNT(*) as purchase_count
            FROM products p
            JOIN orderitem oi1 ON p.id = oi1.product_id
            JOIN orderitem oi2 ON oi1.order_id = oi2.order_id
            WHERE oi2.product_id = %s AND p.id != %s AND p.stock > 0
            GROUP BY p.id
            ORDER BY purchase_count DESC
            LIMIT %s
            """
            
            cursor.execute(query, (product_id, product_id, limit))
            results = cursor.fetchall()
            conn.close()
            
            recommendations = []
            for product in results:
                recommendation = ProductRecommendation(
                    product_id=product['id'],
                    name=product['name'],
                    price=product['price'],
                    brand=product['brand'],
                    category=product['category'],
                    rating=product['rating'],
                    picture=product['picture'],
                    score=0.7,
                    reason=f"Often bought together ({product['purchase_count']} times)"
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Fallback co-purchase recommendations error: {str(e)}")
            return []