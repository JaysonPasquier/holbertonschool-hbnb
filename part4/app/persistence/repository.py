import logging
from abc import ABC, abstractmethod
from app.models.database import db

logger = logging.getLogger(__name__)

class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}

    def add(self, obj):
        logger.debug(f"Adding item with ID {obj.id} to repository")
        self._storage[obj.id] = obj
        logger.debug(f"Repository now contains {len(self._storage)} items")
        return obj

    def get(self, obj_id):
        logger.debug(f"Fetching item with ID {obj_id}")
        obj = self._storage.get(obj_id)
        if obj:
            logger.debug(f"Found item with ID {obj_id}")
        else:
            logger.debug(f"No item found with ID {obj_id}")
        return obj

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        if obj_id in self._storage:
            obj = self._storage[obj_id]
            for key, value in data.items():
                setattr(obj, key, value)
            logger.debug(f"Updated item with ID {obj_id}")
            return obj
        logger.debug(f"Failed to update: no item with ID {obj_id}")
        return None

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]
            logger.debug(f"Deleted item with ID {obj_id}")
            return True
        logger.debug(f"Failed to delete: no item with ID {obj_id}")
        return False

    def get_by_attribute(self, attr_name, attr_value):
        logger.debug(f"Searching for item with {attr_name}={attr_value}")
        for obj in self._storage.values():
            if getattr(obj, attr_name, None) == attr_value:
                logger.debug(f"Found item with {attr_name}={attr_value}")
                return obj
        logger.debug(f"No item found with {attr_name}={attr_value}")
        return None


class SQLAlchemyRepository(Repository):
    def __init__(self, model_class):
        self.model_class = model_class

    def add(self, obj):
        logger.debug(f"Adding {self.model_class.__name__} with ID {obj.id} to database")
        db.session.add(obj)
        db.session.commit()
        return obj

    def get(self, obj_id):
        logger.debug(f"Fetching {self.model_class.__name__} with ID {obj_id}")
        return self.model_class.query.get(obj_id)

    def get_all(self):
        logger.debug(f"Fetching all {self.model_class.__name__} records")
        return self.model_class.query.all()

    def update(self, obj_id, data):
        logger.debug(f"Updating {self.model_class.__name__} with ID {obj_id}")
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.session.commit()
            return obj
        return None

    def delete(self, obj_id):
        logger.debug(f"Deleting {self.model_class.__name__} with ID {obj_id}")
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        logger.debug(f"Searching for {self.model_class.__name__} with {attr_name}={attr_value}")
        return self.model_class.query.filter(getattr(self.model_class, attr_name) == attr_value).first()

    def update_object(self, obj):
        """
        Update an existing object in the database
        """
        from app.models.database import db
        try:
            db.session.add(obj)
            db.session.commit()
            return obj
        except Exception as e:
            db.session.rollback()
            raise e