import logging
from typing import Any, Dict, List, Type, TypeVar, Union

from django.db.models import Model, QuerySet

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Model)


def get_model_instance(
    model_class: Type[T],
    id: Union[int, None] = None,
    name: Union[str, None] = None,
    name_field: str = 'name',
    **kwargs: Any,
) -> Union[T, None]:
    """
    Get a model instance by ID or name with additional filters.

    Args:
        model_class: The Django model class
        id: ID of the instance
        name: Name of the instance
        name_field: The field name to use for name lookup (default: 'name')
        **kwargs: Additional filters to apply

    Returns:
        Model instance or None if not found
    """
    if id is not None and name is not None:
        raise ValueError('Only one of id or name should be provided')
    if id is None and name is None and not kwargs:
        raise ValueError('Either id, name, or additional filters must be provided')

    try:
        filters = {}
        if id is not None:
            filters['id'] = id
        if name is not None:
            filters[name_field] = name
        filters.update(kwargs)

        return model_class.objects.get(**filters)
    except model_class.DoesNotExist:
        logger.warning(
            f'{model_class.__name__} not found ' f'(id={id}, {name_field}={name}, filters={kwargs})'
        )
        return None


def get_model_instances_bulk(
    model_class: Type[T],
    ids: Union[List[int], None] = None,
    names: Union[List[str], None] = None,
    name_field: str = 'name',
    **kwargs: Any,
) -> Union[Dict[int, T], Dict[str, T]]:
    """
    Get multiple model instances by IDs or names in one query with additional filters.

    Args:
        model_class: The Django model class
        ids: List of instance IDs
        names: List of instance names
        name_field: The field name to use for name lookup (default: 'name')
        **kwargs: Additional filters to apply

    Returns:
        Dictionary mapping IDs/names to model instances
    """
    if ids is not None and names is not None:
        raise ValueError('Only one of ids or names should be provided')
    if ids is None and names is None and not kwargs:
        raise ValueError('Either ids, names, or additional filters must be provided')

    if ids is not None:
        return model_class.objects.filter(id__in=ids, **kwargs).in_bulk()
    if names is not None:
        return {
            getattr(item, name_field): item
            for item in model_class.objects.filter(**{f'{name_field}__in': names}, **kwargs)
        }
    return {item.id: item for item in model_class.objects.filter(**kwargs)}


def get_model_queryset(model_class: Type[T], **kwargs: Any) -> QuerySet[T]:
    """
    Get a base queryset for a model with optional filters.

    Args:
        model_class: The Django model class
        **kwargs: Filters to apply to the queryset

    Returns:
        Django QuerySet
    """
    return model_class.objects.filter(**kwargs)


def create_model_instance(model_class: Type[T], **kwargs: Any) -> T:
    """
    Create a new model instance.

    Args:
        model_class: The Django model class
        **kwargs: Fields and values for the new instance

    Returns:
        Newly created model instance
    """
    # Validate that all fields exist in the model
    model_fields = {f.name for f in model_class._meta.get_fields()}
    invalid_fields = set(kwargs.keys()) - model_fields
    if invalid_fields:
        raise ValueError(f'Invalid fields for {model_class.__name__}: {invalid_fields}')

    return model_class.objects.create(**kwargs)


def update_model_instance(instance: T, **kwargs: Any) -> T:
    """
    Update an existing model instance.

    Args:
        instance: The model instance to update
        **kwargs: Fields and values to update

    Returns:
        Updated model instance
    """
    # Get all field information once
    meta = instance._meta
    model_fields = {f.name: f for f in meta.get_fields()}

    # Validate that all fields exist in the model
    invalid_fields = set(kwargs.keys()) - model_fields.keys()
    if invalid_fields:
        raise ValueError(f'Invalid fields for {instance.__class__.__name__}: {invalid_fields}')

    # Validate and set field values in a single loop
    for field, value in kwargs.items():
        field_obj = model_fields[field]
        if hasattr(field_obj, 'validate'):
            field_obj.validate(value, instance)
        setattr(instance, field, value)

    instance.save()
    return instance
