# Roadmap for rtfparse

- Rework the CLI. The original reason I wrote rtfparse was to decapsulate HTML from MS Outlook email files. Much of the current CLI serves the purpose of extracting the email body and attachments. This introduced dependency with non-free license (yes, I consider GPL non-free) so that rtfparse currently has a license conflict. By modifying the CLI such that it expects an RTF file (rather than Outlook's .msg file) we shall get rid of that conflict. For extracting content out of Outlook messages, [msg-extractor][msg-extractor]'s own CLI shall be used and done in a separate step.
- Build solid test code
    - introduce end-to-end tests with [behave][behave]
    - bring in some good test material (call for test material)
- Hand over the further development and maintenance of this project to somebody with more free time and investment in RTF than me. By migrating from Windows to FreeBSD, Outlook messages and RTFs have left my life. My incentive to work a tool I'm not personally using is currently very low.

[msg-extractor]: https://github.com/TeamMsgExtractor/msg-extractor
[behave]: https://behave.readthedocs.io/en/stable/
