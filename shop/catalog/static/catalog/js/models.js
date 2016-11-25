var BaseModel = Backbone.Model.extend({
});


var UserModel = BaseModel.extend({
    urlRoot: '/api/v1/user/',
    defaults: {
    }
}); 

var ItemModel = BaseModel.extend({
    urlRoot: '/api/v1/item/',
    defaults: {
    },
    idAttribute: '_id'
}); 

var BaseCollection = Backbone.Collection.extend({
});


var ItemCollection = BaseCollection.extend({
    url: '/api/v1/item/',
    model: ItemModel
});