var Controller = Backbone.Router.extend({
	routes: {
		"login": "login",
		"logout": "logout",
		"": "items",
		"items": "items",
		"items/:id": "item_detail",
		"reg": "reg",
		"confirm?id=:id&hash=:hash": "confirm",
	},

	login: function(){
		if(lview != null){
			lview.render();
		}
	},

	logout: function(){
		if(oview != null){
			oview.render();
		}
	},

	items: function(){
		if(iview != null){
			iview.render();
		}
	},

	item_detail: function(id){
		if(idview != null){
			idview.render(id);
		}
	},

	reg: function(){
		if(rview != null){
			rview.render();
		}
	},

	confirm: function(id, hash){
		if(cview != null){
			cview.render(id, hash);
		}
	}
});

var controller = new Controller();

Backbone.history.start();
