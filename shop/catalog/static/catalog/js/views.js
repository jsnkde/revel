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
            	$("#loginError").text("Login failed");
            	console.log("login failed");
            }
        }); 
	},
	
});

var LogoutView = Backbone.View.extend({
	render: function(){
		Cookies.remove('username');
		Cookies.remove('api_key');
		Cookies.remove('cart');
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

	events:{
		"click #random-order": "random"
	},

	random: function(){
		var cmd = new CommandModel();
		var self = this;
		Backbone.Tastypie.apiKey = {
            username: Cookies.get('username'),
            key: Cookies.get('api_key')
        }; 
        cmd.fetch({
        	success: function(model, response, options){
        		self.retrieve(response.objects[0].order_id);
        	},
        	error: function(model, response, options){
        		console.log("random failure");
        	}
        });
	},

	retrieve: function(id){
		var order = new OrderModel({id: id});
		var self = this;
		order.fetch({
			success: function(model, response, options){
				if(response.done != true){
					self.retrieve(id);
				} else {
					var rtmp = _.template($('#random-order-template').html());
					$("#random-order-container").html(rtmp({order_items:response.items, total_price: response.total_price, suname: Cookies.get('username'), order_id: id}));
				}
        	},
        	error: function(model, response, options){
        		self.retrieve(id);
        	}
		});
	}
});

var OrdersView = Backbone.View.extend({
	el: $("#container"),

	collection: new OrderCollection(), 

	template: _.template($('#ordersTemplate').html()),

	fetchSuccess: function(collection, response, options){
		$(this.el).html(this.template({collection: this.collection.toJSON(), suname: Cookies.get('username')}));
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
                console.log('orders fetch failure');
            }
		});	
	}
});

var CartView = Backbone.View.extend({
	el: $("#container"),

	template: _.template($('#cartTemplate').html()),

	fetchSuccess: function(model, response, options){
		$(this.el).html(this.template({order: response, suname: Cookies.get('username')}));
	},

	fetchError: function(model, response, options){
		$(this.el).html(this.template({order: undefined, suname: Cookies.get('username')}));
	},

	render: function(){        
        if(Cookies.get('cart') == undefined){
        	this.fetchError(undefined, undefined, undefined);
        	return;
        }

		var self = this;
		Backbone.Tastypie.apiKey = {
            username: Cookies.get('username'),
            key: Cookies.get('api_key')
        }; 

        this.model = new OrderModel({id: Cookies.get('cart')});
		this.model.fetch({
			success: function(model, response, options) {
                self.fetchSuccess(model, response, options);                
            },
            error: function(model, response, options) {
                self.fetchError(model, response, options);  
            }
		});	
	},

	events:{
		"click .btn.del": "action",
		"click .btn.add": "action",
		"click .btn.done": "close"
	},

	action: function(ev){
		var del = $(ev.currentTarget).data('del');
		var add = $(ev.currentTarget).data('add');

		var data = {
			add: add,
			del: del
		};

		var self = this;
		Backbone.Tastypie.apiKey = {
            username: Cookies.get('username'),
            key: Cookies.get('api_key')
        }; 

        if(Cookies.get('cart') == undefined){  
        	this.model = undefined;
        	new_order = new OrderModel();
        	new_order.save({}, {
        		success: function(response){
        			Cookies.set('cart', response.attributes.id)
        			self.action(ev);

        		},
        		error: function(response){
        			console.log("error: " + response);
        		}
        	});
        } else if(this.model == undefined) {
        	this.model = new OrderModel({id: Cookies.get('cart')});
        	this.model.fetch({
        		success: function(model, response, options) {
	                self.action(ev);              
	            },
	            error: function(model, response, options) {
	                console.log("fetch cart failed");
	            }
        	});
        } else {
			this.model.save(data, {
				patch: true, 

				success: function(response){
						notificationService.trigger('renderNav');
						if(del != undefined) { self.render(); }
					},

				error: function(response){
						console.log("cart error");
					}
			});
		}
	}, 

	close: function(){
		if(this.model == undefined){
			return;
		}

		var self = this;

		this.model.save({done: true}, {
			patch: true, 

			success: function(response){
					Cookies.remove('cart');
					notificationService.trigger('renderNav');
					self.render();
				},

			error: function(response){
					console.log("close error");
				}
		});
	}
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
					$("#register").hide();
					$("#register-error").text("Confirmation was sent to " + data.email);
				},
				error: function(response){
					console.log("CreateUser error");
					$("#register-error").text("Registration failed.");
				}
			});
	}

});

var ConfirmationView = Backbone.View.extend({
	render: function(id, hash){
		var data = {
			id: id,
			hash: hash
		};

		this.model = new CreateUserModel({id: id});

		this.model.save(data, {
			patch: true,

			success: function(response){
				console.log("patch success");
			},

			error: function(response){
				console.log("patch failure");
			},
		});

		notificationService.trigger('renderNav');
		controller.navigate("login", true);
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

    fetchSuccess: function(model, response, options){
    	var data = {
			username: Cookies.get('username'),
            cart: response.items.length
		};

		$(this.el).html(this.template({data: data}));
    },

	render: function(){
		var self = this;
		if(Cookies.get('cart') != undefined){
			var current_order = new OrderModel({id: Cookies.get('cart')});
			current_order.fetch({
				success: function(model, response, options) {
                	self.fetchSuccess(model, response, options);                
	            },
	            error: function(model, response, options) {
	                console.log('current_order fetch failure');
	            }
			});
		} else {
			var data = {
				username: Cookies.get('username'),
	            cart: 0
			};

			$(this.el).html(this.template({data: data}));
		}
	}
});

login_view = new LoginView();
logout_view = new LogoutView();
items_view = new ItemView();
registration_view = new RegisterView();
item_view = new ItemDetailView();
navigation_view = new NavigationView();
confirmation_view = new ConfirmationView();
orders_view = new OrdersView();
cart_view = new CartView();
