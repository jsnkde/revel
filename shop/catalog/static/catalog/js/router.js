var Controller = Backbone.Router.extend({
	routes: {
		"": "login",
		"items": "items",
		"reg": "reg"
	},

	login: function(){
		if(lview != null){
			lview.render();
		}
	},

	items: function(){
		if(iview != null){
			iview.render();
		}
	},

	reg: function(){
		if(rview != null){
			rview.render();
		}
	}
});

var controller = new Controller();

Backbone.history.start();
