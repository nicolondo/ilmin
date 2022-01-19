odoo.define('ilmin_theme.website_shop', function (require) {
'use strict';
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var wSaleUtils = require('website_sale.utils');

   require("web.dom_ready");


    $(".quick_add_to_cart").unbind().click(function (ev) {
        ev.preventDefault();
        var $aSubmit = $(ev.currentTarget);
        var frm = $aSubmit.closest('tr');
        var parent = $aSubmit.closest('.card-body');
        var $trash = frm.find('.action-trash');
        var product_product = frm.parent().parent().parent().find('input[name="product_id"]').attr("value");
        var product_price = parseFloat(frm.find('.product_variant_price').find(".oe_currency_value").text());
        var $input = frm.find('input[name="add_qty"]')
        var line_id = frm.parent().parent().parent().find('input[name="line_id"]').attr("value");
        var $qtyNavBar = $(".my_cart_qty");
        var $amountNavBar = $(".my_cart_amount");
        var data = {cart_quantity:parseFloat($qtyNavBar.text() || 0),cart_total:parseFloat($amountNavBar.text() || 0)};
        var min = parseFloat($input.data("min") || 0);
        var max = parseFloat($input.data("max") || Infinity);
        var previousQty = parseFloat($input.val() || 0, 2);
        var previousTotal = data.cart_total;
        var $ineTotal = frm.find('.line_total_price')
        var $productTmplineTotal = parent.find('.total_product')

        if($aSubmit.hasClass('add_mass')){
            var add_qty = parseFloat($aSubmit.attr('qty'));
            var quantity =add_qty + previousQty;
            var add_amount =add_qty * product_price;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;

            if (newQty !== previousQty & newQty > 0) {


                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':newQty}).then(function(result) {
                   $input.val(newQty).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                   $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)

                   $input.parent().removeClass('invisible');
                $trash.removeClass('invisible');

                });
            }else{

                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':0}).then(function(result) {
                   $input.val(0).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                   $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)

                   $input.parent().addClass('invisible');
                $trash.addClass('invisible');

                });

            }

        }else if ($aSubmit.hasClass('js_add_cart_json_ilmin')) {
            var add_or_remove_qty = ($aSubmit.has(".fa-minus").length ? -1 : 1);
            var add_amount =add_or_remove_qty * product_price;
            var quantity =  add_or_remove_qty+ previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
            data.cart_quantity = data.cart_quantity + add_or_remove_qty


            if (newQty !== previousQty & newQty > 0) {


                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':newQty}).then(function(result) {
                   $input.val(newQty).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                                      $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)

                   $input.parent().removeClass('invisible');
                    $trash.removeClass('invisible');

                });
            }else{

                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':0}).then(function(result) {
                   $input.val(0).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                                      $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)

                   $input.parent().addClass('invisible');
                   $trash.addClass('invisible');

                });

            }

        }else if ($aSubmit.hasClass('js_delete_product_ilmin')) {
            var newQty = 0

            if (newQty !== previousQty) {


                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':0}).then(function(result) {
                   $input.val(newQty).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                   $input.parent().addClass('invisible');
                   $trash.addClass('invisible');
                   $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)


                });


            }
        }




    });

    $(".my_cart_icon").click(function (ev) {
        $(".cart_ilmin").toggle('slow')
    })

     $("input[name='pickadresse']").click(function (ev) {
         var $old = $('.shippement_selected');
        $old.removeClass('shippement_selected');

        var $new = $(ev.currentTarget).closest('.card');
        $new.addClass('shippement_selected');
         $("#address_on_payment").toggle('show')
        $("#cart_lines_ilmin").toggle('show')
        $(".cart_ilmin_footer").toggle('show')
    })

    $("#choose_address").click(function (ev) {
        $("#address_on_payment").toggle('show')
        $("#cart_lines_ilmin").toggle('show')
        $(".cart_ilmin_footer").toggle('show')

    })

  $("#add_adress").click(function (ev) {
        $("#ilmin_add_edit_adress").toggle('show')
    })

    $("#create_new_address").click(function (ev) {
        $("#ilmin_add_edit_adress").toggle('show')
        $("#address_on_payment").toggle('show')
        $("#cart_lines_ilmin").toggle('show')
        $(".cart_ilmin_footer").toggle('show')
    })

});
