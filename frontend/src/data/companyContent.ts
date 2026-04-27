export interface OptOutLink {
  url: string;
  label: string;
  notes?: string;
}

export interface OptOutInfo {
  settingsUrl?: string;
  trainingOptOut?: OptOutLink;
  trainingOptOutNote?: string;
  deletion?: OptOutLink;
  notes?: string;
}

export interface CompanyContent {
  explainer?: string;
  optOut?: OptOutInfo;
}

export const companyContent: Record<string, CompanyContent> = {
  meta: {
    explainer:
      "Operates the largest cross-site tracking network outside of Google, fed by the Meta Pixel embedded across millions of third-party sites and apps. Long history of regulatory action — the FTC consent decree, multiple GDPR fines — and has steadily expanded data use to train Llama and Meta AI on user posts, photos, and reels.",
    optOut: {
      settingsUrl: "https://accountscenter.meta.com/",
      trainingOptOut: {
        url: "https://www.facebook.com/privacy/genai",
        label: "Privacy Center → Generative AI at Meta → Object to your information being used",
        notes:
          "EU users have a stronger objection right under GDPR; US users may find the form's scope limited. Covers public posts, not private messages.",
      },
      deletion: {
        url: "https://accountscenter.meta.com/info_and_permissions/",
        label: "Accounts Center → Your information and permissions → Delete account",
      },
      notes:
        "Opting out of in-app data use does not stop tracking on third-party sites with the Meta Pixel installed.",
    },
  },
  openai: {
    explainer:
      "ChatGPT free and Plus tiers train on user conversations by default; the API does not. Has a deletion process, but stresses that deletion does not necessarily remove your data from already-trained models. Increasingly under scrutiny over scraped training data — the New York Times lawsuit is the high-profile example.",
    optOut: {
      settingsUrl: "https://chatgpt.com/",
      trainingOptOut: {
        url: "https://chatgpt.com/",
        label: "ChatGPT → Settings → Data controls → Improve the model for everyone (toggle off)",
        notes:
          "Toggling this off also disables chat history. API and Enterprise data is not used for training by default.",
      },
      deletion: {
        url: "https://privacy.openai.com/",
        label: "privacy.openai.com → Make a privacy request → Delete your data",
      },
      notes:
        "“Delete” means the data is removed going forward. It does not remove your prior content from already-trained models.",
    },
  },
  anthropic: {
    explainer:
      "Markets itself on safety and minimal data retention. Consumer Claude (Free, Pro, Max) does not train on your conversations by default. API and Workbench data is not used for training by default either — Anthropic has historically been one of the most conservative defaults in the industry.",
    optOut: {
      settingsUrl: "https://privacy.anthropic.com/",
      trainingOptOutNote:
        "Anthropic does not train on consumer or API conversations by default — there is generally no opt-out toggle to flip. Some opt-in research programs exist; see the Privacy Center for details.",
      deletion: {
        url: "https://privacy.anthropic.com/",
        label: "privacy.anthropic.com → Submit a privacy request → Delete my data",
      },
    },
  },
  google: {
    explainer:
      "Operates the most pervasive consumer data collection infrastructure in existence — Search, YouTube, Maps, Gmail, Android, Chrome, Workspace. AI training data sources for Gemini are not fully disclosed; consumer Gemini activity is logged into My Activity unless you turn that off.",
    optOut: {
      settingsUrl: "https://myaccount.google.com/data-and-privacy",
      trainingOptOut: {
        url: "https://myaccount.google.com/activitycontrols",
        label: "Activity Controls → Gemini Apps Activity (turn off + auto-delete)",
        notes:
          "Turning off Gemini Apps Activity stops new conversations from being saved and reviewed. Existing data must be deleted separately.",
      },
      deletion: {
        url: "https://myaccount.google.com/delete-services-or-account",
        label: "My Account → Data & privacy → Delete a service or your account",
      },
      notes:
        "Activity Controls do not stop all logging — security and ad-system telemetry is retained regardless of these toggles.",
    },
  },
  microsoft: {
    explainer:
      "Major OpenAI investor and integrates GPT-class models throughout its stack — Copilot, Bing, Office, Windows. Enterprise contracts (Azure OpenAI, Copilot for Business) come with strong data-isolation guarantees. Consumer Copilot and Bing have looser commitments and have shifted multiple times.",
    optOut: {
      settingsUrl: "https://account.microsoft.com/privacy",
      trainingOptOut: {
        url: "https://account.microsoft.com/privacy",
        label: "Privacy dashboard → Search & browse history / Voice activity (review and delete)",
        notes:
          "Microsoft does not currently expose a single “do not train” toggle for consumer Copilot. Deleting your activity history is the closest available control.",
      },
      deletion: {
        url: "https://account.microsoft.com/privacy",
        label: "Privacy dashboard → per-service deletion controls",
      },
    },
  },
  apple: {
    explainer:
      "Markets privacy as a core product feature. Apple Intelligence runs on-device for most tasks and uses Private Cloud Compute for the rest, with the strongest data-minimization commitments of any major platform. The catch: those commitments have not been independently audited end-to-end.",
    optOut: {
      settingsUrl: "https://privacy.apple.com/",
      trainingOptOutNote:
        "Apple states it does not use customer data to train its foundation models. There is no separate AI training opt-out because the default is no use. Siri history can be reviewed and deleted in Settings → Siri & Search.",
      deletion: {
        url: "https://privacy.apple.com/",
        label: "privacy.apple.com → Request to delete your account",
      },
    },
  },
  amazon: {
    explainer:
      "Operates AWS (which hosts a substantial fraction of the internet's data), Amazon.com (purchase + browsing history), Ring (video surveillance), and Alexa (voice). Has shared Ring footage with law enforcement under various policies. Trains Titan and Nova models with terms that have shifted as the AI program has scaled.",
    optOut: {
      settingsUrl: "https://www.amazon.com/gp/help/customer/display.html?nodeId=GVYFUSSRRMAYTGCG",
      trainingOptOut: {
        url: "https://www.amazon.com/alexaprivacy",
        label: "Alexa Privacy → Manage Your Alexa Data → Help improve Alexa (toggle off)",
        notes:
          "Alexa-specific. Amazon does not currently expose a single training opt-out covering all of its AI products.",
      },
      deletion: {
        url: "https://www.amazon.com/gp/help/customer/contact-us",
        label: "Customer Service → Close my Amazon account",
      },
    },
  },
  reddit: {
    explainer:
      "Sold a multi-year licensing deal to Google to train AI models on Reddit content, and signed a similar deal with OpenAI. Public posts are explicitly considered training material under the Terms of Service. Deleted accounts can still appear in archives, and the API changes of 2023 effectively ended free third-party access.",
    optOut: {
      settingsUrl: "https://www.reddit.com/settings/privacy",
      trainingOptOutNote:
        "Reddit has no formal AI training opt-out for users. Public posts are licensed for training under the Terms of Service. The only practical defenses are deleting individual posts before account deletion or never posting publicly.",
      deletion: {
        url: "https://www.reddit.com/settings/account",
        label: "Settings → Account → Delete account",
        notes:
          "Deleted comments may persist in third-party archives (Pushshift-style), and licensed training data already shared with partners is not recalled.",
      },
    },
  },
  adobe: {
    explainer:
      "Trains Adobe Firefly on Adobe Stock content. Expanded its terms in 2024 to claim broader access to user content for content moderation, faced public backlash, and partially walked it back. Creative Cloud users have long been the de facto test case for what counts as “user content” when an AI training program scales.",
    optOut: {
      settingsUrl: "https://account.adobe.com/privacy",
      trainingOptOut: {
        url: "https://account.adobe.com/privacy",
        label: "Account → Privacy and personal data → Content analysis (toggle off)",
        notes:
          "Disables analysis of your Creative Cloud content for product improvement, which Adobe has stated includes generative AI features.",
      },
      deletion: {
        url: "https://account.adobe.com/privacy",
        label: "Account → Privacy and personal data → Delete account",
      },
    },
  },
  x: {
    explainer:
      "Operates with the loosest public privacy stance of the major AI companies. Public posts and direct messages are used to train Grok by default, with an opt-out toggle that ships off. Has dismantled most of the trust & safety reporting Twitter previously published, and the privacy policy has been rewritten multiple times since the 2022 acquisition.",
    optOut: {
      settingsUrl: "https://x.com/settings/account",
      trainingOptOut: {
        url: "https://x.com/settings/grok_settings",
        label: "Settings → Privacy and safety → Grok → Allow your posts and interactions with Grok to be used (toggle off)",
        notes:
          "Default is on. Setting only takes effect for content posted after the toggle is flipped.",
      },
      deletion: {
        url: "https://x.com/settings/your_twitter_data",
        label: "Settings → Your account → Deactivate your account",
      },
    },
  },
  linkedin: {
    explainer:
      "Owned by Microsoft. Trains generative AI features on user profiles, posts, and activity. Rolled out a new training program in 2024 with EU users opted-in by default, paused after regulatory pushback, then re-launched. The opt-out exists but is account-level and was not announced clearly to users.",
    optOut: {
      settingsUrl: "https://www.linkedin.com/mypreferences/d/categories/privacy",
      trainingOptOut: {
        url: "https://www.linkedin.com/mypreferences/d/settings/data-for-ai-improvement",
        label: "Settings → Data privacy → Data for Generative AI Improvement (toggle off)",
      },
      deletion: {
        url: "https://www.linkedin.com/mypreferences/d/account",
        label: "Settings → Account preferences → Account management → Close account",
      },
    },
  },
  tiktok: {
    explainer:
      "Owned by ByteDance. Subject to ongoing US regulatory and divestiture pressure due to Chinese ownership. Collects unusually granular behavioral data — watch-time-per-frame, scroll pauses, device-level identifiers. Project Texas, the public commitment to isolate US data, remains partially implemented.",
    optOut: {
      settingsUrl: "https://www.tiktok.com/setting",
      trainingOptOutNote:
        "TikTok does not currently expose a clear AI training opt-out for users. Personalized ads and data sharing can be reduced under Privacy → Ads, but training-specific controls are not separately surfaced.",
      deletion: {
        url: "https://www.tiktok.com/setting/account-control",
        label: "Settings → Manage account → Delete account",
      },
    },
  },
  snap: {
    explainer:
      "Most messages are stored briefly by design, and ephemerality is marketed as a privacy feature. My AI (the chatbot) trains on user conversations with that bot. Augmented-reality features collect detailed face and environment data, used in some cases to train Snap's AR/AI models.",
    optOut: {
      settingsUrl: "https://accounts.snapchat.com/",
      trainingOptOut: {
        url: "https://help.snapchat.com/",
        label: "Snapchat app → Profile → My AI → Clear data",
        notes:
          "Resets My AI conversation data. Does not retroactively remove data already used in training.",
      },
      deletion: {
        url: "https://accounts.snapchat.com/accounts/delete_account",
        label: "Snapchat Accounts portal → Delete my account",
      },
    },
  },
  spotify: {
    explainer:
      "Collects extensive listening behavior used to power recommendations and a lucrative third-party data licensing business. AI features (AI DJ, AI Playlist) have rolled out without comprehensive privacy policy updates. Public disclosure on training data sources is limited.",
    optOut: {
      settingsUrl: "https://www.spotify.com/account/privacy/",
      trainingOptOutNote:
        "Spotify does not currently expose a public AI training opt-out. Personalized ads and data sharing for marketing partners can be limited under Account → Privacy settings.",
      deletion: {
        url: "https://support.spotify.com/contact-spotify-support/",
        label: "Spotify Support → Account → Close account",
      },
    },
  },
  netflix: {
    explainer:
      "Among the most restrained data collectors of the major platforms — viewing history is the primary data they hold. Does not run a major user-data advertising business, though the ad-supported tier introduced in 2022 has loosened that and brought new third-party partners into the data flow.",
    optOut: {
      settingsUrl: "https://www.netflix.com/account",
      trainingOptOutNote:
        "Netflix does not market a generative AI product trained on user content. Recommendation models train on viewing data; there is no formal opt-out short of cancelling the account.",
      deletion: {
        url: "https://www.netflix.com/cancelplan",
        label: "Account → Cancel membership (data is retained for 10 months by default after cancellation)",
      },
    },
  },
  pinterest: {
    explainer:
      "Image-heavy ad platform with shopping integrations. Has signed AI training data licensing deals; user-generated boards and pins are subject to broad license terms granted in the Terms of Service. Default-on personalization is the norm.",
    optOut: {
      settingsUrl: "https://www.pinterest.com/settings/privacy-and-data",
      trainingOptOut: {
        url: "https://www.pinterest.com/settings/privacy-and-data",
        label: "Settings → Privacy and data → Use of your data for AI (toggle off)",
        notes: "Available in some regions; rollout has not been uniform globally.",
      },
      deletion: {
        url: "https://www.pinterest.com/settings/account-management",
        label: "Settings → Account management → Delete account",
      },
    },
  },
  samsung: {
    explainer:
      "Operates phones, smart TVs, smart appliances, and the Knox enterprise platform — collecting data across all of them. Has a complicated history with smart TV data collection, including the 2015 controversy over voice data sent to third-party services without clear disclosure. Galaxy AI features expanded the AI data flow significantly in 2024.",
    optOut: {
      settingsUrl: "https://account.samsung.com/membership/personal/info",
      trainingOptOut: {
        url: "https://account.samsung.com/membership/personal/info",
        label: "On-device: Settings → Galaxy AI → Online AI features (limit) and Process data only on device (where supported)",
        notes:
          "Galaxy AI features differ by device and region. The on-device-only setting reduces but does not eliminate cloud processing.",
      },
      deletion: {
        url: "https://account.samsung.com/membership/personal/info",
        label: "Samsung Account → Account management → Delete account",
      },
    },
  },
  discord: {
    explainer:
      "Stores voice and chat data with retention policies that vary by Discord plan and server type. Runs an automated content moderation pipeline that scans messages for policy violations. Subject to legal-process requests for chat histories at large scale.",
    optOut: {
      settingsUrl: "https://discord.com/login",
      trainingOptOut: {
        url: "https://discord.com/login",
        label: "User Settings → Privacy & Safety → Use data to improve Discord (toggle off)",
      },
      deletion: {
        url: "https://discord.com/login",
        label: "User Settings → My Account → Delete Account",
      },
    },
  },
  uber: {
    explainer:
      "Holds detailed location histories spanning hundreds of millions of trips. Faced a major 2017 breach cover-up and FTC consent decree. Driver and rider data is shared with various third parties for fraud detection, dispute resolution, and operations.",
    optOut: {
      settingsUrl: "https://privacy.uber.com/",
      trainingOptOutNote:
        "Uber does not run a public generative-AI product trained on user data prominently. There is no separate training opt-out exposed today.",
      deletion: {
        url: "https://privacy.uber.com/",
        label: "Uber Privacy Center → Delete your account",
      },
    },
  },
  paypal: {
    explainer:
      "Holds high-stakes financial transaction data with regulatory protections (US, EU). Updated terms in 2023 to broaden data sharing with affiliates for ad targeting; the resulting opt-out was both available and hard to find, which became a small public controversy.",
    optOut: {
      settingsUrl: "https://www.paypal.com/myaccount/privacy",
      trainingOptOutNote:
        "PayPal does not run a public generative-AI product trained on user data. The relevant control here is data sharing for advertising, not AI training.",
      deletion: {
        url: "https://www.paypal.com/myaccount/settings/",
        label: "Settings → Account → Close account",
      },
    },
  },
};
