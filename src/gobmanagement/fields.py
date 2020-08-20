from graphene_sqlalchemy import SQLAlchemyConnectionField


class LogFilterConnectionField(SQLAlchemyConnectionField):
    RELAY_ARGS = ['first', 'last', 'before', 'after', 'sort']

    @classmethod
    def get_query(cls, model, info, **args):
        query = super(LogFilterConnectionField, cls).get_query(model, info, **args)

        # Do not return DATAWARNING, DATAERROR, DATAINFO
        query = query.filter(getattr(model, 'level').notlike('DATA%'))
        for field, value in args.items():
            if field not in cls.RELAY_ARGS:
                query = query.filter(getattr(model, field) == value)
        return query
