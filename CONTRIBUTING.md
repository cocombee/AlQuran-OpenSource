# Contributing

We welcome improvements to portability, audio quality checks, accessibility and production documentation.

1. Open an issue describing the problem and the proposed change.
2. Use synthetic or independently licensed test inputs. Keep credentials, private account information, copyrighted translation corpora and real production media out of pull requests.
3. Keep paid service requests explicit. Offline checks must not generate narration or mutate an active Resolve project.
4. Explain how the change was verified and which platform it supports.
5. Run the offline tests and submit a pull request with a focused scope. Keep all changes for that review in one final commit when requested.

Contributions of original code and documentation are accepted under the MIT License. Only submit material you have the right to license. Third-party content must have a documented compatible license or stay outside this repository.

For text or pronunciation reports, provide the surah and ayah reference, source edition/version and a concise description. Do not silently replace canonical Arabic or quoted translation text. Word recognition is supporting evidence; a human must verify the meaning, complete spoken words and the final listening result.

Useful starting issues: add a portable Windows pipe reader to the Resolve helper; expand synthetic evidence/receipt coverage; generalize account-specific request limits; create an accessible listening interface with appropriate source permissions.
