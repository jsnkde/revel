var notificationService = {};
_.extend(notificationService, Backbone.Events);

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

		this.model.clear();
		this.model.fetch({
            headers: {'Authorization': ("Basic ".concat(btoa(auth_str)))}, 

            success: function(model, response, options) {
            	Cookies.set('username', response.objects[0].username);
            	Cookies.set('api_key', response.objects[0].key);    
				notificationService.trigger('renderNav');   	         	
                controller.navigate("items", true);
            },

            error: function(model, response, options) {
            	console.log("login failed");
            }
        }); 
	},
	
});

var LogoutView = Backbone.View.extend({
	render: function(){
		Cookies.remove('username');
		Cookies.remove('api_key');
		notificationService.trigger('renderNav');
		controller.navigate("login", true);
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
                self.fetchSuccess(collection, response, options);                
            },
            error: function(collection, response, options) {
                console.log('item fetch failure');
            }
		});
				
	},

	initialize : function () {
        this.listenTo(notificationService, 'show', this.show);
    },

    show: function () {
    },
});

var RegisterView = Backbone.View.extend({
	el: $("#container"),

	model: new CreateUserModel(),

	template: _.template($('#registerTemplate').html()),

	render: function(){
		$(this.el).html(this.template());
	},

	events:{
		"click #reg": "reg"
	},

	reg: function(){
		var data = {
			username: $("#usname").val(),
			email: $("#email").val(),
			password: $("#psword").val(),
		};

		if(!data.username || !data.email || !data.password){
			$("#register-error").text("Fill empty fields.");
			return;
		}

		this.model.save(data, 
			{ 
				dataType: 'text',
				validate: true,

				success: function(response){
					console.log("CreateUser success");
					controller.navigate("login", true);
				},
				error: function(response){
					console.log("CreateUser error");
					$("#register-error").text("Registration failed.");
				}
			});
	}

});

var ItemDetailView = Backbone.View.extend({
	el: $("#container"),

	template: _.template($("#itemDetailTemplate").html()),

	iid: undefined,

	fetchSuccess: function(model, response, options){		
		$(this.el).html(this.template({model: this.model.toJSON(), username: Cookies.get('username')}));
	},

	events:{
		"click #submit-review": "submit"
	},

	submit: function(){
		var data = {
			name: $("#review-username").val(),
			rating: $("#review-rating input[type='radio']:checked").val(),
			text: $("#review-text").val(),
			item: this.iid
		};
		
		if(!data.name || !data.rating || !data.text){
			$("#review-error").text("Fill empty fields.");
			return;
		}

		review = new ReviewModel();
		var self = this;
		review.save(data,
			{
				success: function(response){
					self.render(self.iid);
				},
				error: function(response){
					console.log("review save error");
				}
			});
	},

	render: function(id){
		var self = this;
		Backbone.Tastypie.apiKey = {
            username: Cookies.get('username'),
            key: Cookies.get('api_key')
        }; 
        
        this.iid = id;
        this.model = new ItemModel({id: id});
		this.model.fetch({
			success: function(model, response, options) {
                self.fetchSuccess(model, response, options);                
            },
            error: function(model, response, options) {
                console.log('item fetch failure');
            }
		});
	}
});

var NavigationView = Backbone.View.extend({
	el: $("#navigation"),

	template: _.template($("#navTemplate").html()),

	initialize: function(){
		this.listenTo(notificationService, 'renderNav', this.render);
        this.render();
    },

	render: function(){
		var data = {
			username: Cookies.get('username'),
            key: Cookies.get('api_key')
		};
		
		$(this.el).html(this.template({data: data}));
	}
});

lview = new LoginView();
oview = new LogoutView();
iview = new ItemView();
rview = new RegisterView();
idview = new ItemDetailView();
nview = new NavigationView();
