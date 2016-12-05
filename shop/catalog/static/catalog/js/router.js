var Controller = Backbone.Router.extend({
	routes: {
		"login": "login",
		"logout": "logout",
		"": "items",
		"items": "items",
		"items/:id": "item_detail",
		"reg": "reg",
		"confirm?id=:id&hash=:hash": "confirm",
		"orders": "orders",
		"cart": "cart"
	},

	login: function(){
		if(login_view != null){
			login_view.render();
		}
	},

	logout: function(){
		if(logout_view != null){
			logout_view.render();
		}
	},

	items: function(){
		if(items_view != null){
			items_view.render();
		}
	},

	item_detail: function(id){
		if(item_view != null){
			item_view.render(id);
		}
	},

	reg: function(){
		if(registration_view != null){
			registration_view.render();
		}
	},

	confirm: function(id, hash){
		if(confirmation_view != null){
			confirmation_view.render(id, hash);
		}
	},

	orders: function(){
		if(orders_view != null){
			orders_view.render();
		}
	},

	cart: function(){
		if(cart_view != null){
			cart_view.render();
		}
	},
});

var controller = new Controller();

Backbone.history.start();
