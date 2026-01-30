"use strict";
(self.webpackChunksirius_gateway_mobisite_ang_frnt = self.webpackChunksirius_gateway_mobisite_ang_frnt || []).push([[162], {
    3162: function(h, d, o) {
        o.r(d),
        o.d(d, {
            LoginModule: function() {
                return f
            }
        });
        var l = o(8551)
          , s = o(6213)
          , r = o(7972)
          , i = o(2837)
          , e = [{
            path: "",
            children: [{
                path: "sendsms",
                loadChildren: function() {
                    return Promise.all([o.e(592), o.e(169)]).then(o.bind(o, 5169)).then(function(t) {
                        return t.SendSmsModule
                    })
                }
            }, {
                path: "verify",
                loadChildren: function() {
                    return Promise.all([o.e(592), o.e(826)]).then(o.bind(o, 8826)).then(function(t) {
                        return t.VerifySmsModule
                    })
                }
            }, {
                path: "**",
                redirectTo: "sendsms"
            }]
        }]
          , a = function() {
            var n = (0,
            l.Z)(function t() {
                (0,
                s.Z)(this, t)
            });
            return n.\u0275fac = function(u) {
                return new (u || n)
            }
            ,
            n.\u0275mod = i.oAB({
                type: n
            }),
            n.\u0275inj = i.cJS({
                imports: [[r.Bz.forChild(e)], r.Bz]
            }),
            n
        }()
          , f = function() {
            var n = (0,
            l.Z)(function t() {
                (0,
                s.Z)(this, t)
            });
            return n.\u0275fac = function(u) {
                return new (u || n)
            }
            ,
            n.\u0275mod = i.oAB({
                type: n
            }),
            n.\u0275inj = i.cJS({
                imports: [[a]]
            }),
            n
        }()
    }
}]);
