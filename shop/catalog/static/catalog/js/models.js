var BaseModel = Backbone.Model.extend({
});

var UserModel = BaseModel.extend({
    urlRoot: '/api/v1/user/',
    defaults: {
    }
}); 

var CreateUserModel = BaseModel.extend({
    urlRoot: '/api/v1/create_user/',
    defaults: {
    },
    idAttribute: "id"
}); 

var ItemModel = BaseModel.extend({
    urlRoot: '/api/v1/item/',
    defaults: {
    },
}); 

var ReviewModel = BaseModel.extend({
    urlRoot: '/api/v1/review/',
    defaults: {
    },
}); 

var CommandModel = BaseModel.extend({
    urlRoot: '/api/v1/command/',
    defaults: {
    },
}); 

var OrderModel = BaseModel.extend({
    urlRoot: '/api/v1/order/',
    defaults: {
    },
});

var BaseCollection = Backbone.Collection.extend({
});

var ItemCollection = BaseCollection.extend({
    url: '/api/v1/item/',
    model: ItemModel
});

var OrderCollection = BaseCollection.extend({
    url: '/api/v1/order/',
    model: OrderModel
});