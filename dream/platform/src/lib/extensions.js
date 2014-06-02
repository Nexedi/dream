/* ========================= GALLERY WIDGET ========================= */
(function ($) {

  $.widget("mobile.carousel", {

    options: {
      bullets: null,
      bulletsPos: null,
      inset: null,
      captions: null,
      captionpos: null,
      captiontheme: null,
      carouseltransition: null,
      heading: "h1,h2,h3,h4,h5,h6,legend"
    },

    _transitionEndEvents : "webkitTransitionEnd oTransitionEnd " +
      "otransitionend transitionend msTransitionEnd",

    _create: function () {
      var el = this.element[0],
        o = this.options,
        getAttrFixed = $.mobile.getAttribute;

      // only time we read the DOM config
      o.inset = getAttrFixed(el, "inset", true) || false;
      o.carouseltransition = getAttrFixed(el, "transition", true) || "slide";
      o.bullets = getAttrFixed(el, "bullets", true) || true;
      o.captions = getAttrFixed(el, "captions", true) || false;

      if (o.captions) {
        o.captionspos = getAttrFixed(el, "captions-pos", true) || "bottom";
        o.captionstheme = getAttrFixed(el, "captions-theme", true) || "a";
      }
      if (o.bullets) {
        o.bulletsPos = getAttrFixed(el, "bulletsPos", true) || "bottom";
      }

      this.refresh(true);
    },

    refresh: function (create) {
      var o = this.options,
        el = this.element,
        items = el.children(),
        fragment = document.createDocumentFragment(),
        classes = "ui-carousel",
        barrel,
        label,
        radio,
        item,
        i,
        containsLinks,
        captionsHeading,
        captionsContent;

      // loop over images
      for (i = 0; i < items.length; i += 1) {
        item = items[i];

        // create captions
        if (o.captions) {
          containsLinks = item.children.length === 1
            && item.children[0].tagName === "A";
          captionsContent = $(item)
            .find(containsLinks ? "a *" : "*")
            .not("img")
            .wrap("<div class='ui-carousel-captions-content ui-bar-" +
              o.captionstheme + " ui-carousel-captions-" + o.captionspos +
              "'></div>")
            .parent();

          captionsHeading = captionsContent.find(o.heading).addClass(
            "ui-carousel-captions-heading"
          );
        }

        // create radios
        if (o.bullets) {
          // TODO: do this in jQuery...
          radio = document.createElement("input");
          radio.setAttribute("type", 'radio');
          radio.setAttribute("name", 'radio-' + this.uuid);
          radio.setAttribute("value", 'radio-' + this.uuid + '-' + i);
          if (i === 0) {
            radio.checked = true;
            $(item).addClass("ui-carousel-active");
          }
          // and use data()
          radio.reference = $(item);

          label = document.createElement("label");
          label.setAttribute("data-" + $.mobile.ns + "iconpos", "notext");
          label.appendChild(radio);

          fragment.appendChild(label);
        }
      }

      if (o.inset) {
        classes += " ui-carousel-inset";
      }

      if (o.captions) {
        classes += " ui-carousel-captions";
      }

      if (o.bullets) {
        classes += " ui-carousel-bullets";
        barrel = $("<div id='ui-carousel-barrel-" + this.uuid +
          "' class='ui-carousel-controls ui-carousel-controls-" +
          o.bulletsPos + "' />");

        while (fragment.firstChild) {
          // browser hangs up if calling this inside append()
          $(fragment.firstChild).children().checkboxradio();
          barrel.append(
            fragment.firstChild
          );
        }
        // remove existing barrel
        if (create === undefined) {
          $("#ui-carousel-barrel-" + this.uuid).remove();
        }
        // this always needs to go before the slider
        el[o.bulletsPos === "top" ? "before" : "after"](barrel);

        this._on(barrel.find("input"), { change: "_onChange"});
      }

      // all set, add classes
      el.addClass(classes);
    },

//       _handleKeydown: function( event ) {
//         var index = this._value();
//         if ( this.options.disabled ) {
//           return;
//         }
//
//         // In all cases prevent the default and mark the handle as active
//         switch ( event.keyCode ) {
//           case $.mobile.keyCode.RIGHT:
//           case $.mobile.keyCode.LEFT:
//             event.preventDefault();
//
//             if ( !this._keySliding ) {
//               this._keySliding = true;
//               this.handle.addClass( "ui-state-active" );
//             }
//
//             break;
//         }
//
//         // move the slider according to the keypress
//         switch ( event.keyCode ) {
//           case $.mobile.keyCode.RIGHT:
//             this.refresh( index + this.step );
//             break;
//           case $.mobile.keyCode.LEFT:
//             this.refresh( index - this.step );
//             break;
//         }
//       }, // remove active mark
//
//       _handleKeyup: function(/* event */) {
//         if ( this._keySliding ) {
//           this._keySliding = false;
//         }
//       },

//       _bindSwipeEvents: function() {
//         var self = this,
//           area = self.element;
//
//         // on swipe, change to the next/previous image
//         if( !!self.options.swipeClose ) {
//           if ( self.options.position === "left" ) {
//             area.on( "swipeleft.carousel", function(/* e */) {
//               // self.close();
//             });
//           } else {
//             area.on( "swiperight.carousel", function(/* e */) {
//               // self.close();
//             });
//           }
//         }
//       },

    _completeTransition: function (current, next, events) {
      var self = this,
        o = self.options;
      next.removeClass("in out " + o.carouseltransition)
          .off(events);
      current
        .on(events, self._cleanupTransition(current, events));
    },

    _cleanupTransition: function (current, events) {
      var self = this,
        o = self.options,
        classes = o.carouseltransition + " out in";
      current.removeClass(classes);
      current.removeClass("ui-carousel-active").off(events);
    },

    _onChange: function (e) {
      var self = this,
        events = self._transitionEndEvents,
        el = self.element,
        o = self.options,
        currentActive = el.children().filter(".ui-carousel-active"),
        nextActive = e.target.reference,
        //classes = o.carouseltransition + " out in",
        transition = $.mobile._maybeDegradeTransition(o.carouseltransition);

      // click on active radio
      if (nextActive.hasClass("ui-carousel-active")) {
        return;
      }

      // initialize
      nextActive
        .on(events, self._completeTransition(
          currentActive,
          nextActive,
          events
        ));
      nextActive
        .addClass(transition + " ui-carousel-active in ");

    }
  });

}(jQuery));
/* tranistion workflow
// first slide
if (init) {
  current.removeClass("ui-carousel-active in out reverse slide")
  next.css('z-index','-10')
    .addClass("ui-carousel-active ui-carousel-opaque")
    .css('z-index','')

    if (transition !== "none") {
      // > once animation is complete!
      // current.removeClass("ui-carousel-active in out reverse slide")
      // next.removeClass("out in reverse slide")

      next.removeClass("ui-carousel-opaque")
      .addClass("slide in reverse")

    } else {
      current.removeClass("ui-carousel-active in out reverse slide")
      next.removeClass("out in reverse slide")
    }
} else {
  // > once animation is complete
  current.removeClass("ui-carousel-active in out reverse slide")
  next.css('z-index','-10')
    .addClass("ui-carousel-active ui-carousel-opaque")
    .css('z-index','')

    if (transition !== "none") {
      // > once animation is complete!
      // current.removeClass("ui-carousel-active in out reverse slide")
      // next.removeClass("out in reverse slide")

      next.removeClass("ui-carousel-opaque")
      .addClass("slide in reverse")

    } else {
      current.removeClass("ui-carousel-active in out reverse slide")
      next.removeClass("out in reverse slide")
    }
  current.addClass("slide out reverse");
}
*/

/* ========================= ACTION BUTTON EXTENSION ==================== */
(function () {

  $.widget("mobile.textinput", $.mobile.textinput, {

    options: {
      actionBtn: false,
      actionBtnText: "Search",
      actionBtnIcon: "search"
    },

    _create: function () {
      this._super();
      if (!!this.options.actionBtn || this.isSearch) {
        this._addActionBtn();
      }
    },

    actionButton: function () {

      return $("<a href='#' class='ui-input-action ui-btn ui-icon-" +
        this.options.actionBtnIcon + " ui-btn-icon-notext ui-corner-all" +
        "' title='" + this.options.actionBtnText + "'>" +
        this.options.actionBtnText + "</a>");
    },

    _addActionBtn: function () {

      if (!this.options.enhanced) {
        this._enhanceAction();
      }

      $.extend(this, {
        _actionBtn: this.widget().find("a.ui-input-action")
      });

    },

    _enhanceAction: function () {
      this.actionButton().appendTo(this.widget());
      this.widget().addClass(
        "ui-input-has-action ui-input-search-no-pseudo"
      );
    },

    _setOptions: function (options) {
      this._super(options);

      if (options.actionBtn !== undefined &&
          !this.element.is("textarea, :jqmData(type='range')")) {
        if (options.actionBtn) {
          this._addActionBtn();
        } else {
          this._destroyAction();
        }
      }

      if (options.clearBtnText !== undefined &&
          this._actionBtn !== undefined) {
        this._actionBtn.text(options.clearBtnText);
      }
    },

    _destroyAction: function () {
      this.element.removeClass("ui-input-has-clear");
      this._actionBtn.remove();
    },

    _destroy: function () {
      this._super();
      this._destroyAction();
    }

  });


}());
/* ============================= TABLE ====================================*/
(function( $, undefined ) {

$.widget( "mobile.table", {
  options: {
    classes: {
      table: "ui-table"
    },
    enhanced: false
  },

  _create: function() {
    if ( !this.options.enhanced ) {
      this.element.addClass( this.options.classes.table );
    }

    // extend here, assign on refresh > _setHeaders
    $.extend( this, {

      // Expose headers and allHeaders properties on the widget
      // headers references the THs within the first TR in the table
      headers: undefined,

      // allHeaders references headers, plus all THs in the thead, which may
      // include several rows, or not
      allHeaders: undefined
    });

    this._refresh( true );
  },

  _setHeaders: function() {
    var trs = this.element.find( "thead tr" );

    this.headers = this.element.find( "tr:eq(0)" ).children();
    this.allHeaders = this.headers.add( trs.children() );
  },

  refresh: function() {
    this._refresh();
  },

  rebuild: $.noop,

  _refresh: function( /* create */ ) {
    var table = this.element,
      trs = table.find( "thead tr" );

    // updating headers on refresh (fixes #5880)
    this._setHeaders();

    // Iterate over the trs
    trs.each( function() {
      var columnCount = 0;

      // Iterate over the children of the tr
      $( this ).children().each( function() {
        var span = parseInt( $.mobile.getAttribute( this, "colspan" ), 10 ),
          selector = ":nth-child(" + ( columnCount + 1 ) + ")",
          j;

        this.setAttribute( "data-" + $.mobile.ns + "colstart", columnCount + 1 );

        if ( span ) {
          for( j = 0; j < span - 1; j++ ) {
            columnCount++;
            selector += ", :nth-child(" + ( columnCount + 1 ) + ")";
          }
        }

        // Store "cells" data on header as a reference to all cells in the
        // same column as this TH
        $( this ).jqmData( "cells", table.find( "tr" ).not( trs.eq( 0 ) ).not( this ).children( selector ) );

        columnCount++;
      });
    });
  }
});

})( jQuery );


(function( $, undefined ) {

$.widget( "mobile.table", $.mobile.table, {
  options: {
    mode: "columntoggle",
    columnBtnTheme: null,
    columnPopupTheme: null,
    columnBtnText: "Columns...",
    columnBtnIcon: "Search",
    sort: null,
    wrap: null,
    topGrid: null,
    bottomGrid: null,
    classes: $.extend( $.mobile.table.prototype.options.classes, {
      popup: "ui-table-columntoggle-popup",
      columnBtn: "ui-table-columntoggle-btn",
      priorityPrefix: "ui-table-priority-",
      columnToggleTable: "ui-table-columntoggle"
    })
  },

  _create: function() {
    this._super();

    if( this.options.mode !== "columntoggle" ) {
      return;
    }

    $.extend( this, {
      _menu: null
    });

    if( this.options.enhanced ) {
      this._menu = this.document.find( this._id() + "-popup" ).children().first();
    } else {
      this._menu = this._enhanceColToggle();
      this.element.addClass( this.options.classes.columnToggleTable );
    }

    this._setupEvents();

    this._setToggleState();
  },

  _id: function() {
    return ( this.element.attr( "id" ) || ( this.widgetName + this.uuid ) );
  },

  _setupEvents: function() {
    //NOTE: inputs are bound in bindToggles,
    // so it can be called on refresh, too

    // update column toggles on resize
    this._on( $.mobile.window, {
      throttledresize: "_setToggleState"
    });
  },

  _bindToggles: function( menu ) {
    var inputs = menu.find( "input" );

    this._on( inputs, {
      change: "_menuInputChange"
    });
  },

  _addToggles: function( menu, keep ) {
    var opts = this.options;

    // allow update of menu on refresh (fixes #5880)
    if ( !keep ) {
      menu.empty();
    }

    // create the hide/show toggles
    this.headers.not( "td" ).each( function() {
      var header = $( this ),
        priority = $.mobile.getAttribute( this, "priority", true ),
        cells = header.add( header.jqmData( "cells" ) );

      if( priority ) {
        cells.addClass( opts.classes.priorityPrefix + priority );
        if ( !keep ) {
          $("<label><input type='checkbox' checked />" + header.text() + "</label>" )
            .appendTo( menu )
            .children( 0 )
            .jqmData( "cells", cells )
            .checkboxradio( {
              theme: opts.columnPopupTheme
            });
        }
      }
    });

    // set bindings here
    if ( !keep ) {
      this._bindToggles( menu );
    }
  },

  _menuInputChange: function( evt ) {
    var input = $( evt.target ),
      checked = input[ 0 ].checked;

    input.jqmData( "cells" )
      .toggleClass( "ui-table-cell-hidden", !checked )
      .toggleClass( "ui-table-cell-visible", checked );

    if ( input[ 0 ].getAttribute( "locked" ) ) {
      input.removeAttr( "locked" );

      this._unlockCells( input.jqmData( "cells" ) );
    } else {
      input.attr( "locked", true );
    }
  },

  _unlockCells: function( cells ) {
    // allow hide/show via CSS only = remove all toggle-locks
    cells.removeClass( "ui-table-cell-hidden ui-table-cell-visible");
  },

  _toLetter: function (n) {
    return n.toString(26).replace(/./g, function( c ) {
      return String.fromCharCode( c.charCodeAt(0) + ( isNaN( +c ) ? 10 : 49 ));
    });
  },

  _generateWrapper: function ( grids ) {
    return $("<div/>", {
      class: "ui-table-wrapper ui-table-wrapper-inset ui-corner-all"
    }).append($.map(new Array( grids ), function(){
      return $("<div/>");
    })).grid({ grid: grids > 1 ? this._toLetter(grids-2) : "solo" });
  },

  _enhanceColToggle: function() {
    var id , menuButton, popup, menu, front, back, slots, fill, i, sorts, btn, item,
      table = this.element,
      opts = this.options,
      ns = $.mobile.ns,
      fragment = $.mobile.document[ 0 ].createDocumentFragment();

    id = this._id() + "-popup";
    menuButton = $( "<a role='button' href='#" + id + "' " +
      "class='" + opts.classes.columnBtn + " ui-btn ui-btn-" + ( opts.columnBtnTheme || "a" ) + " ui-corner-all ui-shadow ui-mini ui-icon ui-btn-icon-left ui-icon-"+ opts.columnBtnIcon +"' " +
      "data-" + ns + "rel='popup' " +
      "data-" + ns + "icon='" + opts.columnBtnIcon + "' " +
      "data-" + ns + "mini='true'>" + opts.columnBtnText + "</a>" );
    popup = $( "<div data-" + ns + "role='popup' data-" + ns + "role='fieldcontain' class='" + opts.classes.popup + "' id='" + id + "'></div>" );
    menu = $( "<fieldset data-" + ns + "role='controlgroup'></fieldset>" );


    // set extension here, send "false" to trigger build/rebuild
    this._addToggles( menu, false );

    menu.appendTo( popup );

    // wrappers
    // TODO: not nice, should be possible to wrap top with 3 elements
    // and then where do you put the toggle button
    // TODO: also not nice, because no way to latch on the filter
    // TODO: also not nice, because data-slot-id is not used.

    if (opts.wrap) {
      fill = table.parent().find( "div[data-slot]" );

      if (opts.wrap === "both") {
        front = this._generateWrapper( opts.topGrid );
        back = this._generateWrapper( opts.bottomGrid );

        if (fill) {
          slots = front.add( back ).children("div");
          for (i = 0; i < fill.length; i += 1) {
            item = parseFloat(fill.eq(i).jqmData("slot-id"))-1;
            fill.eq(i)
              .find("label")
              .addClass("ui-hidden-accessible")
              .end()
            // skip slot 2
            .appendTo( slots.eq( item || (i === 2 ? 3 : i)) );
          }
        }
        front
          .addClass("ui-table-wrapper-top")
          .children("div").last().append( menuButton[ 0 ] );
        back
          .addClass("ui-table-wrapper-bottom");

        fragment.appendChild( front[ 0 ] );
        fragment.appendChild( popup[ 0 ] );
        // not possible in one-go...
        table.before(fragment)
        table.after(back);

      } else {
        front = this._generateWrapper( opts.topGrid || opts.bottomGrid || 3);

        if (fill.length) {
          slots = front.children("div");

          for (i = 0; i < fill.length; i += 1) {
            fill.eq(i)
              .find("label")
              .addClass("ui-hidden-accessible")
              .end()
            // skip slot 2
            .appendTo( slots.eq( i === 2 ? 3 : i ) );
          }
        }
        front
          .addClass("ui-table-wrapper-top")
          .children("div").last().append( menuButton[ 0 ] );

        fragment.appendChild( front[ 0 ] );
        fragment.appendChild( popup[ 0 ] );

        // not possible in one-go...
        table[ opts.wrap === "top" ? "before" : "after"](fragment)
      }

    // no wrap
    } else {
      fragment.appendChild( popup[ 0 ] );
      fragment.appendChild( menuButton[ 0 ] );

      table.before( fragment );
    }

    if (opts.sort) {
      sorts = table.find( "thead tr th[data-sortable]" );
      btn = $("<a />", {
        class: "ui-sortable ui-btn ui-icon-sort-down ui-icon ui-btn-icon-right",
      });
      sorts.each(function(i, el) {
        var $el = $(el);
        $el.html( btn.clone().text( $el.text() ) );
      });
    }

    popup.popup().children( "fieldset" ).controlgroup();

    // always return the menu
    return menu;
  },

  rebuild: function() {
    this._super();

    if ( this.options.mode === "columntoggle" ) {
      // NOTE: rebuild passes "false", while refresh passes "undefined"
      // both refresh the table, but inside addToggles, !false will be true,
      // so a rebuild call can be indentified
      this._refresh( false );
    }
  },

  _refresh: function( create ) {
    this._super( create );

    if ( !create && this.options.mode === "columntoggle" ) {
      // columns not being replaced must be cleared from input toggle-locks
      this._unlockCells( this.allHeaders );

      // update columntoggles and cells
      this._addToggles( this._menu, create );

      // check/uncheck
      this._setToggleState();
    }
  },

  _setToggleState: function() {
    this._menu.find( "input" ).each( function() {
      var checkbox = $( this );

      this.checked = checkbox.jqmData( "cells" ).eq( 0 ).css( "display" ) === "table-cell";
      checkbox.checkboxradio( "refresh" );
    });
  },

  _destroy: function() {
    this._super();
  }
});

})( jQuery );

(function( $, undefined ) {

$.widget( "mobile.table", $.mobile.table, {
  options: {
    mode: "reflow",
    classes: $.extend( $.mobile.table.prototype.options.classes, {
      reflowTable: "ui-table-reflow",
      cellLabels: "ui-table-cell-label"
    })
  },

  _create: function() {
    this._super();

    // If it's not reflow mode, return here.
    if( this.options.mode !== "reflow" ) {
      return;
    }

    if( !this.options.enhanced ) {
      this.element.addClass( this.options.classes.reflowTable );

      this._updateReflow();
    }
  },

  rebuild: function() {
    this._super();

    if ( this.options.mode === "reflow" ) {
      this._refresh( false );
    }
  },

  _refresh: function( create ) {
    this._super( create );
    if ( !create && this.options.mode === "reflow" ) {
      this._updateReflow( );
    }
  },

  _updateReflow: function() {
    var table = this,
      opts = this.options;

    // get headers in reverse order so that top-level headers are appended last
    $( table.allHeaders.get().reverse() ).each( function() {
      var cells = $( this ).jqmData( "cells" ),
        colstart = $.mobile.getAttribute( this, "colstart", true ),
        hierarchyClass = cells.not( this ).filter( "thead th" ).length && " ui-table-cell-label-top",
        text = $( this ).text(),
        iteration, filter;

        if ( text !== ""  ) {

          if( hierarchyClass ) {
            iteration = parseInt( this.getAttribute( "colspan" ), 10 );
            filter = "";

            if ( iteration ){
              filter = "td:nth-child("+ iteration +"n + " + ( colstart ) +")";
            }

            table._addLabels( cells.filter( filter ), opts.classes.cellLabels + hierarchyClass, text );
          } else {
            table._addLabels( cells, opts.classes.cellLabels, text );
          }

        }
    });
  },

  _addLabels: function( cells, label, text ) {
    // .not fixes #6006
    cells.not( ":has(b." + label + ")" ).prepend( "<b class='" + label + "'>" + text + "</b>"  );
  }
});

})( jQuery );
/* ====================================== COLLAPSIBLE =====================*/
(function( $, undefined ) {

var rInitialLetter = /([A-Z])/g;

$.widget( "mobile.collapsible", {
  options: {
    enhanced: false,
    expandCueText: null,
    collapseCueText: null,
    collapsed: true,
    heading: "h1,h2,h3,h4,h5,h6,legend",
    icon: null,
    collapsedIcon: null,
    expandedIcon: null,
    iconpos: null,
    theme: null,
    contentTheme: null,
    inset: null,
    corners: null,
    mini: null
  },

  _create: function() {
    var elem = this.element,
      ui = {
        accordion: elem
          .closest( ":jqmData(role='collapsible-set')" +
            ( $.mobile.collapsibleset ? ", :mobile-collapsibleset" : "" ) )
          .addClass( "ui-collapsible-set" )
      };

    $.extend( this, {
      _ui: ui
    });

    if ( this.options.enhanced ) {
      ui.heading = $( ".ui-collapsible-heading", this.element[ 0 ] );
      ui.content = ui.heading.next();
      ui.anchor = $( "a", ui.heading[ 0 ] ).first();
      ui.status = ui.anchor.children( ".ui-collapsible-heading-status" );
    } else {
      this._enhance( elem, ui );
    }

    this._on( ui.heading, {
      "tap": function() {
        ui.heading.find( "a" ).first().addClass( $.mobile.activeBtnClass );
      },

      "click": function( event ) {
        this._handleExpandCollapse( !ui.heading.hasClass( "ui-collapsible-heading-collapsed" ) );
        event.preventDefault();
        event.stopPropagation();
      }
    });
  },

  // Adjust the keys inside options for inherited values
  _getOptions: function( options ) {
    var key,
      accordion = this._ui.accordion,
      accordionWidget = this._ui.accordionWidget;

    // Copy options
    options = $.extend( {}, options );

    if ( accordion.length && !accordionWidget ) {
      this._ui.accordionWidget =
      accordionWidget = accordion.data( "mobile-collapsibleset" );
    }

    for ( key in options ) {

      // Retrieve the option value first from the options object passed in and, if
      // null, from the parent accordion or, if that's null too, or if there's no
      // parent accordion, then from the defaults.
      options[ key ] =
        ( options[ key ] != null ) ? options[ key ] :
        ( accordionWidget ) ? accordionWidget.options[ key ] :
        accordion.length ? $.mobile.getAttribute( accordion[ 0 ],
          key.replace( rInitialLetter, "-$1" ).toLowerCase(), true ):
        null;

      if ( null == options[ key ] ) {
        options[ key ] = $.mobile.collapsible.defaults[ key ];
      }
    }

    return options;
  },

  _themeClassFromOption: function( prefix, value ) {
    return ( value ? ( value === "none" ? "" : prefix + value ) : "" );
  },

  _enhance: function( elem, ui ) {
    var iconclass,
      opts = this._getOptions( this.options ),
      contentThemeClass = this._themeClassFromOption( "ui-body-", opts.contentTheme );

    elem.addClass( "ui-collapsible " +
      ( opts.inset ? "ui-collapsible-inset " : "" ) +
      ( opts.inset && opts.corners ? "ui-corner-all " : "" ) +
      ( contentThemeClass ? "ui-collapsible-themed-content " : "" ) );
    ui.originalHeading = elem.children( this.options.heading ).first(),
    ui.content = elem
      .wrapInner( "<div " +
        "class='ui-collapsible-content " +
        contentThemeClass + "'></div>" )
      .children( ".ui-collapsible-content" ),
    ui.heading = ui.originalHeading;

    // Replace collapsibleHeading if it's a legend
    if ( ui.heading.is( "legend" ) ) {
      ui.heading = $( "<div role='heading'>"+ ui.heading.html() +"</div>" );
      ui.placeholder = $( "<div><!-- placeholder for legend --></div>" ).insertBefore( ui.originalHeading );
      ui.originalHeading.remove();
    }

    iconclass = ( opts.icon === false ? "ui-collapsible-hide-icon " : "" ) +
      ( opts.collapsed ? ( opts.collapsedIcon ? "ui-icon-" + opts.collapsedIcon : "" ) :
      ( opts.expandedIcon ? "ui-icon-" + opts.expandedIcon : "" ));

    ui.status = $( "<span class='ui-collapsible-heading-status'></span>" );
    ui.anchor = ui.heading
      .detach()
      //modify markup & attributes
      .addClass( "ui-collapsible-heading" )
      .append( ui.status )
      .wrapInner( "<a href='#' class='ui-collapsible-heading-toggle'></a>" )
      .find( "a" )
        .first()
        .addClass( "ui-btn " +
          ( iconclass ? iconclass + " " : "" ) +
          ( iconclass ? ( "ui-btn-icon-" +
            ( opts.iconpos === "right" ? "right" : "left" ) ) +
            " " : "" ) +
          this._themeClassFromOption( "ui-btn-", opts.theme ) + " " +
          ( opts.mini ? "ui-mini " : "" ) );

    //drop heading in before content
    ui.heading.insertBefore( ui.content );

    this._handleExpandCollapse( this.options.collapsed );

    return ui;
  },

  refresh: function() {
    var key, options = {};

    for ( key in $.mobile.collapsible.defaults ) {
      options[ key ] = this.options[ key ];
    }

    this._setOptions( options );
  },

  _setOptions: function( options ) {
    var isCollapsed, newTheme, oldTheme,
      elem = this.element,
      currentOpts = this.options,
      ui = this._ui,
      anchor = ui.anchor,
      status = ui.status,
      opts = this._getOptions( options );

    // First and foremost we need to make sure the collapsible is in the proper
    // state, in case somebody decided to change the collapsed option at the
    // same time as another option
    if ( options.collapsed !== undefined ) {
      this._handleExpandCollapse( options.collapsed );
    }

    isCollapsed = elem.hasClass( "ui-collapsible-collapsed" );

    // Only options referring to the current state need to be applied right away
    // It is enough to store options covering the alternate in this.options.
    if ( isCollapsed ) {
      if ( opts.expandCueText !== undefined ) {
        status.text( opts.expandCueText );
      }
      if ( opts.collapsedIcon !== undefined ) {
        if ( currentOpts.collapsedIcon ) {
          anchor.removeClass( "ui-icon-" + currentOpts.collapsedIcon );
        }
        if ( opts.collapsedIcon ) {
          anchor.addClass( "ui-icon-" + opts.collapsedIcon );
        }
      }
    } else {
      if ( opts.collapseCueText !== undefined ) {
        status.text( opts.collapseCueText );
      }
      if ( opts.expandedIcon !== undefined ) {
        if ( currentOpts.expandedIcon ) {
          anchor.removeClass( "ui-icon-" + currentOpts.expandedIcon );
        }
        if ( opts.expandedIcon ) {
          anchor.addClass( "ui-icon-" + opts.expandedIcon );
        }
      }
    }

    if ( opts.iconpos !== undefined ) {
      anchor.removeClass( "ui-btn-icon-" + ( currentOpts.iconPos === "right" ? "right" : "left" ) );
      anchor.addClass( "ui-btn-icon-" + ( opts.iconPos === "right" ? "right" : "left" ) );
    }

    if ( opts.theme !== undefined ) {
      oldTheme = this._themeClassFromOption( "ui-btn-", currentOpts.theme );
      newTheme = this._themeClassFromOption( "ui-btn-", opts.theme );
      anchor.removeClass( oldTheme ).addClass( newTheme );
    }

    if ( opts.contentTheme !== undefined ) {
      oldTheme = this._themeClassFromOption( "ui-body-", currentOpts.theme );
      newTheme = this._themeClassFromOption( "ui-body-", opts.theme );
      ui.content.removeClass( oldTheme ).addClass( newTheme );
    }

    // It is important to apply "inset" before corners, because the new value of
    // "inset" can affect whether we display corners or not. Note that setting
    // the "inset" option to false does not cause a change in the value of
    // this.options.corners - it merely causes a change in the interpretation of
    // the value of the "corners" option.
    if ( opts.inset !== undefined ) {
      elem.toggleClass( "ui-collapsible-inset", opts.inset );
      currentOpts.inset = opts.inset;
      if ( !opts.inset ) {
        opts.corners = false;
      }
    }

    if ( opts.corners !== undefined ) {
      elem.toggleClass( "ui-corner-all", currentOpts.inset && opts.corners );
    }

    if ( opts.mini !== undefined ) {
      anchor.toggleClass( "ui-mini", opts.mini );
    }

    this._super( options );
  },

  _handleExpandCollapse: function( isCollapse ) {
    var opts = this._getOptions( this.options ),
      ui = this._ui;

    ui.status.text( isCollapse ? opts.expandCueText : opts.collapseCueText );
    ui.heading
      .toggleClass( "ui-collapsible-heading-collapsed", isCollapse )
      .find( "a" ).first()
      .toggleClass( "ui-icon-" + opts.expandedIcon, !isCollapse )

      // logic or cause same icon for expanded/collapsed state would remove the ui-icon-class
      .toggleClass( "ui-icon-" + opts.collapsedIcon, ( isCollapse || opts.expandedIcon === opts.collapsedIcon ) )
      .removeClass( $.mobile.activeBtnClass );

    this.element.toggleClass( "ui-collapsible-collapsed", isCollapse );
    ui.content
      .toggleClass( "ui-collapsible-content-collapsed", isCollapse )
      .attr( "aria-hidden", isCollapse )
      .trigger( "updatelayout" );
    this.options.collapsed = isCollapse;
    this._trigger( isCollapse ? "collapse" : "expand" );
  },

  expand: function() {
    this._handleExpandCollapse( false );
  },

  collapse: function() {
    this._handleExpandCollapse( true );
  },

  _destroy: function() {
    var ui = this._ui,
      opts = this.options;

    if ( opts.enhanced ) {
      return;
    }

    if ( ui.placeholder ) {
      ui.originalHeading.insertBefore( ui.placeholder );
      ui.placeholder.remove();
      ui.heading.remove();
    } else {
      ui.status.remove();
      ui.heading
        .removeClass( "ui-collapsible-heading ui-collapsible-heading-collapsed" )
        .children()
          .contents()
            .unwrap();
    }

    ui.anchor.contents().unwrap();
    ui.content.contents().unwrap();
    this.element
      .removeClass( "ui-collapsible ui-collapsible-collapsed " +
        "ui-collapsible-themed-content ui-collapsible-inset ui-corner-all" );
  }
});

// Defaults to be used by all instances of collapsible if per-instance values
// are unset or if nothing is specified by way of inheritance from an accordion.
// Note that this hash does not contain options "collapsed" or "heading",
// because those are not inheritable.
$.mobile.collapsible.defaults = {
  expandCueText: " click to expand contents",
  collapseCueText: " click to collapse contents",
  collapsedIcon: "plus",
  expandedIcon: "minus",
  iconpos: "left",
  inset: true,
  corners: true,
  mini: false
};

})( jQuery );
/* ============================= COLLAPSIBLE_SET =========================*/
(function( $, undefined ) {

var childCollapsiblesSelector = ":mobile-collapsible, " + $.mobile.collapsible.initSelector;

$.widget( "mobile.collapsibleset", $.extend( {

  // The initSelector is deprecated as of 1.4.0. In 1.5.0 we will use
  // :jqmData(role='collapsibleset') which will allow us to get rid of the line
  // below altogether, because the autoinit will generate such an initSelector
  initSelector: ":jqmData(role='collapsible-set'),:jqmData(role='collapsibleset')",

  options: $.extend( {
    enhanced: false,
    type: null
  }, $.mobile.collapsible.defaults ),

  _isSetAndClose: function ( parent, allClosed ) {

    if (allClosed) {
      return parent.children().length === parent.children(".ui-collapsible-collapsed").length;
    }
    return parent.is( ":mobile-collapsibleset, :jqmData(role='collapsible-set')" );
  },

  _handleCollapsibleExpand: function( event ) {
    var closestCollapsible = $( event.target ).closest( ".ui-collapsible" ),
      parentElement = closestCollapsible.parent();

    if ( this._isSetAndClose( parentElement ) ) {
      closestCollapsible
        .siblings( ".ui-collapsible:not(.ui-collapsible-collapsed)" )
        .collapsible( "collapse" );

    parentElement.toggleClass("ui-collapsible-set-all-closed", this._isSetAndClose( parentElement, true) );
    }
  },

  _handleCollapsibleCollapse: function ( event ) {
    var closestCollapsible = $( event.target ).closest( ".ui-collapsible" ),
      parentElement = closestCollapsible.parent();

    if ( this._isSetAndClose( parentElement ) ) {
      parentElement.toggleClass("ui-collapsible-set-all-closed", this._isSetAndClose( parentElement, true) );
    }
  },

  _create: function() {
    var elem = this.element,
      opts = this.options;

    $.extend( this, {
      _classes: ""
    });

    if ( !opts.enhanced ) {
      elem.addClass( "ui-collapsible-set " +
        this._themeClassFromOption( "ui-group-theme-", opts.theme ) + " " +
        ( opts.corners && opts.inset ? "ui-corner-all " : "" ) );
      // tabs
      if (opts.type) {
        elem.addClass( "ui-collapsible-tabs" );
      }
      this.element.find( $.mobile.collapsible.initSelector ).collapsible();
    }

    this._on( elem, {
      collapsibleexpand: "_handleCollapsibleExpand",
      collapsiblecollapse: "_handleCollapsibleCollapse"
    } );
  },

  _themeClassFromOption: function( prefix, value ) {
    return ( value ? ( value === "none" ? "" : prefix + value ) : "" );
  },

  _init: function() {
    this._refresh( true );

    // Because the corners are handled by the collapsible itself and the default state is collapsed
    // That was causing https://github.com/jquery/jquery-mobile/issues/4116
    this.element
      .children( childCollapsiblesSelector )
      .filter( ":jqmData(collapsed='false')" )
      .collapsible( "expand" );
  },

  _setOptions: function( options ) {
    var ret,
      elem = this.element,
      themeClass = this._themeClassFromOption( "ui-group-theme-", options.theme );

    if ( themeClass ) {
      elem
        .removeClass( this._themeClassFromOption( "ui-group-theme-", this.options.theme ) )
        .addClass( themeClass );
    }

    if ( options.corners !== undefined ) {
      elem.toggleClass( "ui-corner-all", options.corners );
    }

    ret = this._super( options );
    this.element.children( ":mobile-collapsible" ).collapsible( "refresh" );
    return ret;
  },

  _destroy: function() {
    var el = this.element;

    this._removeFirstLastClasses( el.children( childCollapsiblesSelector ) );
    el
      .removeClass( "ui-collapsible-set ui-corner-all " +
        this._themeClassFromOption( "ui-group-theme", this.options.theme ) )
      .children( ":mobile-collapsible" )
      .collapsible( "destroy" );
  },

  _refresh: function( create ) {
    var collapsiblesInSet = this.element.children( childCollapsiblesSelector );

    this.element.find( $.mobile.collapsible.initSelector ).not( ".ui-collapsible" ).collapsible();

    this._addFirstLastClasses( collapsiblesInSet, this._getVisibles( collapsiblesInSet, create ), create );
  },

  refresh: function() {
    this._refresh( false );
  }
}, $.mobile.behaviors.addFirstLastClasses ) );

})( jQuery );
