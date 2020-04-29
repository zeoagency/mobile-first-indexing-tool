'use strict';
const createLighthouse = require('lighthouse-lambda-node12')

exports.hello = function (event, context, callback) {
    var report =  {
		url : event.url || "https://zeo.org/",
		strategy: event.strategy || 'desktop'
	};
	const config = module.exports = {
        extends: 'lighthouse:default',
        settings: {
            maxWaitForFcp: 35 * 1000,
            maxWaitForLoad: 35 * 1000,
            emulatedFormFactor: 'desktop',
            throttling: {
                // Using a "broadband" connection type
                // Corresponds to "Dense 4G 25th percentile" in https://docs.google.com/document/d/1Ft1Bnq9-t4jK5egLSOc28IL4TvR-Tt0se_1faTA4KTY/edit#heading=h.bb7nfy2x9e5v
                rttMs: 40,
                throughputKbps: 10 * 1024,
                cpuSlowdownMultiplier: 1,
            },
            // Skip the h2 audit so it doesn't lie to us. See https://github.com/GoogleChrome/lighthouse/issues/6539
            skipAudits: ['uses-http2'],
        },
    };

	if (report.strategy == 'mobile') {
        const config = module.exports = {
          extends: 'lighthouse:default',
          settings: {
            maxWaitForFcp: 35 * 1000,
            maxWaitForLoad: 35 * 1000,
            skipAudits: ['uses-http2'],
          },
          audits: [
            'metrics/first-contentful-paint-3g',
          ],
          categories: {
            performance: {
              auditRefs: [
                {id: 'first-contentful-paint-3g', weight: 0},
              ],
            },
          },
        };
    }

    Promise.resolve()
    .then(() => createLighthouse(report.url, { logLevel: 'info',output: 'json' }, config))
    .then(({ chrome, results }) => {
            let resultAudit = results.lhr.audits;
            let resultCategories = results.lhr.categories;
            let obj = {
                "audits" : {
                    "screenshot-thumbnails" : {
                        "details": resultAudit['screenshot-thumbnails'].details
                    },
                    "final-screenshot" : {
                        "details": resultAudit['final-screenshot'].details
                    },
                },
                "categories" : {
                    "performance" : {
                        "score": resultCategories['performance'].score,
                    },
                    "accessibility":{
                        "score":resultCategories['accessibility'].score,
                    },
                    "best-practices":{
                        "score":resultCategories['best-practices'].score,
                    },
                    "seo":{
                        "score":resultCategories['seo'].score,
                    },
                    "pwa":{
                        "score":resultCategories['pwa'].score,
                    }
                }
            };
            for (var key in resultAudit) {
                if (resultAudit[key].score != 0 && resultAudit[key].score != 1 && resultAudit[key].score != null) {
                    obj["audits"][resultAudit[key].id] = resultAudit[key]
                }
            }
            if(obj == null) {
                obj = {
                    "error": "Not found data!"
                }
            }
            chrome.kill().then(() => callback(JSON.stringify(obj)))
            return context.succeed(JSON.stringify(obj));
        })
        .catch((error) => {
            chrome.kill().then(() => callback(error))
            console.log(error)
            var response = {
                status: 400,
                errors: 'Error occured!'
            }
            return context.fail(JSON.stringify(response));
        })
    // Handle other errors
    .catch(callback)
}