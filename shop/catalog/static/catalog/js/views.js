var notificationService = {};
_.extend(notificationService, Backbone.Events);

Backbone.Tastypie.apiKey = {};

var LoginView = Backbone.View.extend({
	el: $("#container"),

	model: new UserModel(),

	template: _.template($('#loginTemplate').html()),

	render: function(){
		$(this.el).html(this.template());
	},

	events:{
		"click #submit": "items"
	},

	items: function(){
		var un = $("#uname").val();
		var pw = $("#pword").val();
		var auth_str = un.concat(':'.concat(pw));

		this.model.fetch({
            headers: {'Authorization': ("Basic ".concat(btoa(auth_str)))}, 

            success: function(model, response, options) {
            	Cookies.set('username', response.objects[0].username);
            	Cookies.set('api_key', response.objects[0].key);       	         	
                controller.navigate("items", true);
            },

            error: function(model, response, options) {
            }
        }); 
	},
	
});

var ItemView = Backbone.View.extend({
	el: $("#container"),

	collection: new ItemCollection(), 

	template: _.template($('#submitTemplate').html()),

	fetchSuccess: function(collection, response, options){
		$(this.el).html(this.template({collection: this.collection.toJSON(), suname: Cookies.get('username'), skey: Cookies.get('api_key')}));
	},

	render: function(){
		var self = this;
		Backbone.Tastypie.apiKey = {
            username: Cookies.get('username'),
            key: Cookies.get('api_key')
        }; 
		this.collection.fetch({
			success: function(collection, response, options) {
                console.log('success');
                self.fetchSuccess(collection, response, options);                
            },
            error: function(collection, response, options) {
                console.log('failure');
            }
		});
				
	},

	initialize : function () {
        this.listenTo(notificationService, 'show', this.show);
    },

    show: function () {
    },
});

lview = new LoginView();
iview = new ItemView();
